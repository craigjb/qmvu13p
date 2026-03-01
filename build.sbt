ThisBuild / version := "0.1"
ThisBuild / scalaVersion := "2.12.18"
ThisBuild / organization := "com.craigjb"
ThisBuild / fork := true

val spinalVersion = "1.13.0"
val spinalCore = "com.github.spinalhdl" %% "spinalhdl-core" % spinalVersion
val spinalLib = "com.github.spinalhdl" %% "spinalhdl-lib" % spinalVersion
val spinalIdslPlugin = compilerPlugin("com.github.spinalhdl" %% "spinalhdl-idsl-plugin" % spinalVersion)

lazy val qmvu13p = (project in file("."))
  .settings(
    name := "spiny",
    Compile / scalaSource := baseDirectory.value / "src" / "spinal",
    libraryDependencies ++= Seq(
      spinalCore,
      spinalLib,
      spinalIdslPlugin,
    ),
    publish / skip := true,
  )
