name := "finshield-spark"
version := "1.0"
scalaVersion := "2.12.18"

val sparkVersion = "3.5.1"

libraryDependencies ++= Seq(
  "org.apache.spark" %% "spark-core"            % sparkVersion % "provided",
  "org.apache.spark" %% "spark-sql"             % sparkVersion % "provided",
  "org.apache.spark" %% "spark-streaming"       % sparkVersion % "provided",
  "org.apache.spark" %% "spark-sql-kafka-0-10"  % sparkVersion,
  "org.apache.spark" %% "spark-hive"            % sparkVersion % "provided"
)

assemblyMergeStrategy in assembly := {
  case PathList("META-INF", _*) => MergeStrategy.discard
  case _                        => MergeStrategy.first
}
