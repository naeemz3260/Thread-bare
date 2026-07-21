// Sample vulnerable Node.js/Express code for scanner demo purposes.
const express = require("express");
const mysql = require("mysql");
const { exec } = require("child_process");
const app = express();

const db = mysql.createConnection({
  host: "localhost",
  user: "root",
  password: "SuperSecret123!", // hardcoded credential
  database: "app_db",
});

// SQL Injection: user input concatenated directly into query
app.get("/user", (req, res) => {
  const userId = req.query.id;
  const query = "SELECT * FROM users WHERE id = " + userId;
  db.query(query, (err, results) => {
    res.json(results);
  });
});

// Reflected XSS: unescaped user input written directly into HTML response
app.get("/search", (req, res) => {
  const term = req.query.q;
  res.send("<h1>Results for: " + term + "</h1>");
});

// Command Injection: user input passed straight to a shell command
app.get("/ping", (req, res) => {
  const host = req.query.host;
  exec("ping -c 1 " + host, (err, stdout) => {
    res.send(stdout);
  });
});

// Insecure deserialization of untrusted JSON into eval
app.post("/config", (req, res) => {
  const raw = req.body.config;
  const parsed = eval("(" + raw + ")");
  res.json(parsed);
});

app.listen(3000);
