# Azure SQL → Spark JDBC: Scala Reference

> **Context:** When running a Spark job in Azure Databricks (Scala) that needs to read from an Azure SQL Database whose connection string is stored as a secret in Azure Key Vault, the secret may be in **ODBC/ADO.NET format** rather than the **JDBC format** that Spark expects. This document captures the Scala utility code that converts between the two.

---

## Driver

Use the **Microsoft JDBC Driver for SQL Server**:

| Property | Value |
|---|---|
| Maven artifact | `com.microsoft.sqlserver:mssql-jdbc` |
| Driver class | `com.microsoft.sqlserver.jdbc.SQLServerDriver` |
| JDBC URL scheme | `jdbc:sqlserver://<host>:1433;database=<db>;…` |

The driver is often pre-installed on Azure Databricks clusters. If not, add it as a cluster library (Maven coordinates above).

---

## What the conversion handles

The connection string stored in Key Vault typically looks like an **ODBC/ADO.NET** string:

```
{ODBC Driver 17 for SQL Server};Server=tcp:my-server.database.windows.net,1433;Database=MyDB;UID=myuser;PWD=secret;Encrypt=yes;
```

Spark requires a **JDBC URL** of the form:

```
jdbc:sqlserver://my-server.database.windows.net:1433;database=MyDB;encrypt=true;trustServerCertificate=false;hostNameInCertificate=*.database.windows.net;loginTimeout=30;
```

Key differences:
- The `{ODBC Driver …}` token must be dropped (it is ODBC-only).
- `Server=tcp:<host>,<port>` → `jdbc:sqlserver://<host>:<port>;`
- `Database=` / `Initial Catalog=` → `database=` in the JDBC URL.
- `UID=` / `User ID=` → separated into `.option("user", …)` on the Spark reader.
- `Encrypt=yes` → `encrypt=true` (JDBC uses boolean strings; also handles the common `Encypt` typo).

---

## Scala utility

```scala
import scala.util.Try

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Normalise "yes"/"no" to "true"/"false" for JDBC boolean properties. */
def toBool(v: String): String = v.trim.toLowerCase match {
  case "yes" | "true"  => "true"
  case "no"  | "false" => "false"
  case other           => other
}

/**
 * Split a semicolon-delimited key=value string into a lower-cased key map.
 * Segments that do not contain "=" (e.g. the ODBC driver token) are ignored.
 */
def parseKvPairs(cs: String): Map[String, String] =
  cs.split(";")
    .map(_.trim)
    .filter(s => s.nonEmpty && s.contains("="))
    .map { kv =>
      val Array(k, v) = kv.split("=", 2)
      k.trim.toLowerCase -> v.trim
    }
    .toMap

/**
 * Strip the "{ODBC Driver …}" segment, parse the remaining key=value pairs,
 * and normalise synonym keys (UID → user id, Encypt → encrypt, etc.).
 */
def normalizeOdbcLikeConnString(raw: String): Map[String, String] = {
  val cleaned = raw
    .split(";")
    .map(_.trim)
    .filter(s => s.nonEmpty && !s.startsWith("{") && !s.endsWith("}"))
    .mkString(";")

  parseKvPairs(cleaned).map { case (k, v) =>
    val nk = k match {
      case "uid"    => "user id"
      case "pwd"    => "password"
      case "encypt" => "encrypt"   // handle the common misspelling
      case other    => other
    }
    nk -> v
  }
}

// ---------------------------------------------------------------------------
// Main conversion function
// ---------------------------------------------------------------------------

/**
 * Convert an ODBC/ADO.NET-style Azure SQL connection string to a Spark JDBC URL.
 *
 * Returns a tuple of:
 *   - the JDBC URL string
 *   - an Option[String] containing the username (if present in the conn string)
 *   - an Option[String] containing the password (if present in the conn string)
 *
 * Example input:
 *   {ODBC Driver 17 for SQL Server};Server=tcp:my-server.database.windows.net,1433;
 *   Database=MyDB;UID=myuser;PWD=secret;Encrypt=yes;
 *
 * Example output URL:
 *   jdbc:sqlserver://my-server.database.windows.net:1433;database=MyDB;
 *   encrypt=true;trustServerCertificate=false;
 *   hostNameInCertificate=*.database.windows.net;loginTimeout=30;
 */
def buildJdbcFromOdbcLike(raw: String): (String, Option[String], Option[String]) = {
  val m = normalizeOdbcLikeConnString(raw)

  // Server=tcp:<host>,<port>  →  host + port
  val serverRaw = m.getOrElse("server", m.getOrElse("data source", ""))
  val serverNoPrefix = serverRaw.stripPrefix("tcp:").stripPrefix("TCP:")
  val (host, port) =
    if (serverNoPrefix.contains(",")) {
      val Array(h, p) = serverNoPrefix.split(",", 2)
      (h, p)
    } else (serverNoPrefix, "1433")

  // Database= or Initial Catalog=
  val db = m.get("database").orElse(m.get("initial catalog")).getOrElse("")

  // Use explicit encrypt value from conn string if present; default to true for Azure SQL
  val encrypt = m.get("encrypt").map(toBool).getOrElse("true")

  val jdbcUrl =
    s"jdbc:sqlserver://$host:$port;" +
      s"database=$db;" +
      s"encrypt=$encrypt;" +
      "trustServerCertificate=false;" +
      "hostNameInCertificate=*.database.windows.net;" +
      "loginTimeout=30;"

  val user = m.get("user id").orElse(m.get("user"))
  val pass = m.get("password")

  (jdbcUrl, user, pass)
}

// ---------------------------------------------------------------------------
// Usage in Azure Databricks
// ---------------------------------------------------------------------------

// 1. Pull the ODBC/ADO.NET connection string from Key Vault-backed secrets.
val raw = dbutils.secrets.get("kv-scope", "sqldb-connection-string")
val (jdbcUrl, userFromConn, passFromConn) = buildJdbcFromOdbcLike(raw)

// 2. If credentials are also stored as separate secrets, those take precedence;
//    otherwise fall back to whatever was parsed from the connection string.
val user = Try(dbutils.secrets.get("kv-scope", "sqldb-user")).toOption.orElse(userFromConn)
val pass = Try(dbutils.secrets.get("kv-scope", "sqldb-pass")).toOption.orElse(passFromConn)

require(
  user.isDefined && pass.isDefined,
  "Missing SQL credentials: set 'sqldb-user'/'sqldb-pass' secrets or include UID/PWD in the connection string."
)

// 3. Spark JDBC read.
val df =
  spark.read
    .format("jdbc")
    .option("url",      jdbcUrl)
    .option("user",     user.get)
    .option("password", pass.get)
    .option("driver",   "com.microsoft.sqlserver.jdbc.SQLServerDriver")
    .option("dbtable",  "dbo.YourTable")   // replace with your target table
    .load()
```

---

## Notes

| Topic | Detail |
|---|---|
| **AAD auth** | If your organisation uses Azure Active Directory (Managed Identity or Service Principal) instead of SQL auth, replace `user`/`password` options with the appropriate `Authentication=…` JDBC property. |
| **Separate credential secrets** | It is best practice to store `UID`/`PWD` as their own Key Vault secrets and keep only the connection-string *structure* (no credentials) in the connection-string secret. |
| **Driver version** | Pin the `mssql-jdbc` version to match your Databricks Runtime. DBR 13+ ships with `12.x`; earlier runtimes use `9.x` or `10.x`. |
| **Private endpoints** | Being in the same subscription/resource group does **not** automatically grant network access. Ensure the Databricks VNet can resolve and reach the SQL private endpoint (or use the public endpoint with firewall rules). |
| **`encrypt=true`** | Required for Azure SQL Database. Never set `trustServerCertificate=true` in production. |
