import readline from "node:readline";

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false,
});

rl.on("line", (line) => {
  const response = {
    server: "echo_server",
    received: line,
  };
  process.stdout.write(`${JSON.stringify(response)}\n`);
});
