import logging
from notion_client import Client
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()


class NotionFetcher:
    def __init__(self):
        self.token =  os.getenv("NOTION_TOKEN")
        self.database_id = os.getenv("DATABASE_ID")
        if not self.token:
            raise ValueError("NOTION_TOKEN not found in environment variables")

        self.client = Client(auth=self.token)

    def fetch_tasks(self) -> List[Dict]:
        tasks = []
        has_more = True
        start_cursor = None

        while has_more:
            try:
                response = self.client.databases.query(
                    database_id=self.database_id, start_cursor=start_cursor)
                tasks.extend(self._process_tasks(response))
                has_more = response.get("has_more", False)
                start_cursor = response.get("next_cursor", None)
            except Exception as e:
                logging.error(f"[NotionFetcher] Error fetching data from Notion: {e}")
                break

        return tasks

    def _process_tasks(self, response) -> List[Dict]:
        tasks = []
        for page in response.get("results", []):
            properties = page["properties"]

            # Extract task name from rich_text property
            task_name_prop = properties.get("Task name", {}) or properties.get("Task Name", {})
            task_name = ""
            if task_name_prop.get("rich_text") and len(task_name_prop.get("rich_text")) > 0:
                task_name = task_name_prop.get("rich_text")[0].get("text", {}).get("content", "")
            
            # Only use "Unnamed Task" if the task name is completely empty
            if not task_name or task_name.strip() == "":
                task_name = "Unnamed Task"
            
            # Extract assignee from people property
            assignee_prop = properties.get("Assignee", {})
            assignee = "Unassigned"
            if "people" in assignee_prop and assignee_prop["people"]:
                assignee = assignee_prop["people"][0].get("name", "Unassigned")
            
            # Extract status from status property
            status_prop = properties.get("Status", {})
            status = "No Status"
            if "status" in status_prop and status_prop["status"]:
                status = status_prop["status"].get("name", "No Status")
            
            # Extract due date from date property
            due_date_prop = properties.get("Due date", {}) or properties.get("Due Date", {})
            due_date = "No Due Date"
            if "date" in due_date_prop and due_date_prop["date"]:
                due_date = due_date_prop["date"].get("start", "No Due Date")

            task = {
                "Task Name": task_name,
                "Assignee": assignee,
                "Status": status,
                "Due Date": due_date,
            }
            tasks.append(task)

        return tasks


