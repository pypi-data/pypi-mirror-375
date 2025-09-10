
# OracleDB MCP Server

[![smithery badge](https://smithery.ai/badge/@rahgadda/oracledb_mcp_server)](https://smithery.ai/server/@rahgadda/oracledb_mcp_server) [![MseeP.ai Security Assessment Badge](https://mseep.net/mseep-audited.png)](https://mseep.ai/app/rahgadda-oracledb-mcp-server)

## Overview
- This project will install `MCP - Model Context Protocol Server`, that provides configured Oracle Database Table/Columns as context to LLM's.
- Using this we can enable LLMs to interact with Oracle Database, Generate SQL Statements and Return Results using LLM prompts.

## Installation
- Install package
  ```bash
  pip install oracledb_mcp_server
  ```
- Create .env in a folder with minimum value of `Oracle DB Connection String`. Sample file available [here](https://raw.githubusercontent.com/rahgadda/oracledb_mcp_server/refs/heads/main/.env)
- Test `oracledb_mcp_server` server using `uv run oracledb_mcp_server` from the above folder.

## Claud Desktop
- Configuration details for Claud Desktop
  ```json
  {
    "mcpServers": {
      "oracledb_mcp_server":{
        "command": "uv",
        "args": ["run","oracledb_mcp_server"],
        "env": {
            "DEBUG":"True",
            "COMMENT_DB_CONNECTION_STRING":"oracle+oracledb://USERNAME:PASSWORD@IP:PORT/?service_name=SERVICENAME",
            "DB_CONNECTION_STRING":"oracle+oracledb://USERNAME:PASSWORD@IP:PORT/?service_name=SERVICENAME",
            "TABLE_WHITE_LIST":"ACCOUNTS,CUS_ACC_RELATIONS,CUSTOMERS",
            "COLUMN_WHITE_LIST":"ACCOUNTS.ACC_AAD_ID,CUS_ACC_RELATIONS.CAR_CUS_ID,CUS_ACC_RELATIONS.CAR_AAD_ID,CUSTOMERS.CUS_ID"
        }
      }
    }
  }
  ```

### Configuration
- List of available environment variables
  - `DEBUG`: Enable debug logging (optional default is False)
  - `COMMENT_DB_CONNECTION_STRING`: Oracle DB connection String for comments. (required)
  - `DB_CONNECTION_STRING`: Oracle DB connection String for execution of queries. (required)
  - `TABLE_WHITE_LIST`: White Listed table names in list format ["table1", "table2"] (required)
  - `COLUMN_WHITE_LIST`: White Listed table-column names in list format ["table.column1", "table.column2"] (required)
  - `QUERY_LIMIT_SIZE`: Default value is 10 records if not provided(optional default is 10)

## Interceptor
```bash
npx @modelcontextprotocol/inspector uv --directory "D:\\MyDev\\mcp\\oracledb_mcp_server" run -m oracledb_mcp_server
```

## Contributing
Contributions are welcome.    
Please feel free to submit a Pull Request.

## License
This project is licensed under the terms of the MIT license.

## Demo
![](./images/demo.png)

## Github Stars
[![Star History Chart](https://api.star-history.com/svg?repos=rahgadda/oracledb_mcp_server=Date)](https://star-history.com/#rahgadda/oracledb_mcp_server&Date)
