from universal_mcp.tools.registry import ToolRegistry
from universal_mcp.agentr.registry import AgentrRegistry
import asyncio
from dotenv import load_dotenv
from tqdm.asyncio import tqdm

load_dotenv()


async def main():
    registry = AgentrRegistry()
    apps = await registry.list_all_apps()
    file_text = ""
    all_file_text = ""
    connected_apps = await registry.list_connected_apps()
    connected_app_ids = [app["app_id"] for app in connected_apps]
    connected_app_ids = list(set(connected_app_ids))
    unconnect_apps = [app["id"] for app in apps if app["id"] not in connected_app_ids]

    # Combine all app IDs with their connection status
    all_apps_with_status = [
        (app_id, "Connected by user") for app_id in connected_app_ids
    ] + [(app_id, "NOT connected by user") for app_id in unconnect_apps]

    # Process all apps with progress bar
    for app_id, status in tqdm(all_apps_with_status, desc="Processing apps"):
        app_tools = await registry.list_tools(app_id)
        important_tools = [tool for tool in app_tools if tool["important"] == True]
        file_text += f"App ID: {app_id} ({status}) \n"
        for tool in important_tools:
            file_text += f" - {tool['name']}: {tool['description']}\n"
        file_text += "\n"
        all_file_text += f"App ID: {app_id} ({status}) \n"
        if len(app_tools) > 50:
            app_tools = important_tools
        for tool in app_tools:
            all_file_text += f" - {tool['name']}: {tool['description']}\n"
        all_file_text += "\n"
    # Write files to the bigtoolcache directory
    output_dir = "src/universal_mcp/agents/bigtoolcache"
    with open(f"{output_dir}/tools_important.txt", "w") as f:
        f.write(file_text)
    with open(f"{output_dir}/tools_all.txt", "w") as f:
        f.write(all_file_text)


asyncio.run(main())
