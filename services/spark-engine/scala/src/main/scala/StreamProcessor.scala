// FinShield AI — Spark Streaming Processor
// Consumes Kafka transactions, computes velocity metrics, writes enriched events back to Kafka.

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.streaming.{OutputMode, Trigger}
import org.apache.spark.sql.types._

object StreamProcessor {

  val transactionSchema: StructType = StructType(Seq(
    StructField("transaction_id",    StringType,  nullable = false),
    StructField("user_id",           StringType),
    StructField("merchant_id",       StringType),
    StructField("amount",            DoubleType),
    StructField("currency",          StringType),
    StructField("transaction_type",  StringType),
    StructField("status",            StringType),
    StructField("device_id",         StringType),
    StructField("ip_address",        StringType),
    StructField("geo_lat",           DoubleType),
    StructField("geo_lon",           DoubleType),
    StructField("region",            StringType),
    StructField("city",              StringType),
    StructField("timestamp",         StringType),
    StructField("is_synthetic_fraud",BooleanType),
    StructField("fraud_scenario",    StringType)
  ))

  def main(args: Array[String]): Unit = {
    val kafkaServers = sys.env.getOrElse("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

    val spark = SparkSession.builder()
      .appName("FinShield-StreamProcessor")
      .config("spark.sql.shuffle.partitions", "8")
      .config("spark.streaming.stopGracefullyOnShutdown", "true")
      .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true")
      .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")
    import spark.implicits._

    // ── 1. Read from Kafka ──────────────────────────────────────────
    val rawStream = spark.readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", kafkaServers)
      .option("subscribe", "transactions")
      .option("startingOffsets", "latest")
      .option("failOnDataLoss", "false")
      .option("maxOffsetsPerTrigger", "5000")
      .load()

    // ── 2. Parse JSON payload ───────────────────────────────────────
    val transactions = rawStream
      .select(
        from_json(col("value").cast(StringType), transactionSchema).as("d"),
        col("timestamp").as("kafka_ts")
      )
      .select("d.*", "kafka_ts")
      .withColumn("event_time", to_timestamp(col("timestamp")))
      .withWatermark("event_time", "2 minutes")

    // ── 3. Velocity window (5-min sliding, 1-min step) ──────────────
    val velocityAgg = transactions
      .groupBy(
        window(col("event_time"), "5 minutes", "1 minute").as("win"),
        col("user_id")
      )
      .agg(
        count("transaction_id").as("txn_count_5m"),
        sum("amount").as("total_amount_5m"),
        countDistinct("device_id").as("unique_devices_5m"),
        countDistinct("merchant_id").as("unique_merchants_5m"),
        avg("amount").as("avg_amount_5m"),
        stddev("amount").as("stddev_amount_5m"),
        max("amount").as("max_amount_5m"),
        collect_set("fraud_scenario").as("fraud_scenarios_seen")
      )
      .withColumn("window_end", col("win.end"))
      .drop("win")

    // ── 4. Write velocity metrics to Kafka ──
    val kafkaSink = velocityAgg
      .select(
        col("user_id").cast(StringType).as("key"),
        to_json(struct(col("*"))).as("value")
      )
      .writeStream
      .format("kafka")
      .option("kafka.bootstrap.servers", kafkaServers)
      .option("topic", "enriched-transactions")
      .option("checkpointLocation", "/tmp/checkpoints/velocity-to-kafka")
      .trigger(Trigger.ProcessingTime("10 seconds"))
      .start()

    // ── 5. Write raw transactions to console (debug) ────────────────
    val consoleSink = transactions
      .select("transaction_id", "user_id", "amount", "transaction_type", "fraud_scenario", "event_time")
      .writeStream
      .format("console")
      .option("truncate", "false")
      .option("numRows", "5")
      .trigger(Trigger.ProcessingTime("30 seconds"))
      .start()

    spark.streams.awaitAnyTermination()
  }
}
