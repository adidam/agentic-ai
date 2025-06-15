import { MCPServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp";
import { z } from "zod";

// Create a new MCP server
const server = new MCPServer();

// add a tool to the server
server.Tool("add", 
    {a: z.number(), b: z.number()},
    async ({a, b}) => ({
        content: [{ type: "text", text: `The sum of ${a} and ${b} is ${a + b}` }]
    })
);

// Create a new resource template
const template = new ResourceTemplate({
    name: "gpt-4o-mini",
});
