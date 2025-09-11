from sempy import fabric
from pyspark.sql import SparkSession

class FabricCache:
    _ws_lh_df = None  # class-level cache

    def __init__(self):
        self.client = fabric.FabricRestClient()
        self.fabric_api = "https://api.fabric.microsoft.com/v1"
        self.headers = {"Content-Type": "application/json"}

    def _safe_get(self, url, context=""):
        """Helper for safe API calls with try/except."""
        try:
            resp = self.client.get(url, headers=self.headers)
            return resp.json().get("value", [])
        except Exception as e:
            print(f"[ERROR] Fabric API call failed ({context}): {e}")
            return []

    def load_workspace_lakehouses(self):
        """Load all workspaces and their lakehouses from Fabric."""

        print("Starting tenant scan for workspaces and lakehouses")

        if FabricCache._ws_lh_df is not None:
            return FabricCache._ws_lh_df

        spark = SparkSession.builder.getOrCreate()
        records = []

        # Get all workspaces safely
        get_workspace_url = f"{self.fabric_api}/workspaces"
        workspaces = self._safe_get(get_workspace_url, context="get_workspaces")

        for ws in workspaces:
            ws_name = ws.get("displayName")
            ws_id = ws.get("id")

            # Get all items in workspace safely
            items_url = f"{self.fabric_api}/workspaces/{ws_id}/items"
            items = self._safe_get(items_url, context=f"workspace {ws_name}")

            for item in items:
                if item.get("type") == "Lakehouse":
                    lh_name = item.get("displayName")
                    lh_id = item.get("id")
                    records.append((ws_name, ws_id, lh_name, lh_id))

        # Build Spark DataFrame
        columns = ["workspaceName", "workspaceId", "lakehouseName", "lakehouseId"]
        FabricCache._ws_lh_df = (spark.createDataFrame(records, columns).dropDuplicates())

        print("Completed tenant scan for workspaces and lakehouses")
        return FabricCache._ws_lh_df

    def get_ws_lh_df(self):
        """Get cached workspace + lakehouse DataFrame."""
        if FabricCache._ws_lh_df is None:
            raise ValueError("Data not loaded from the tenant scan")
        return FabricCache._ws_lh_df

    def getLakehouseId(self, target_workspace_name, target_lakehouse_name):

        ws_lh_df = self.get_ws_lh_df()

        lakehouse_id_row = (
            ws_lh_df
            .filter(
                (ws_lh_df.workspaceName == target_workspace_name) &
                (ws_lh_df.lakehouseName == target_lakehouse_name)
            )
            .select("lakehouseId")
            .collect()
        )

        if lakehouse_id_row:
            lakehouse_id = lakehouse_id_row[0]["lakehouseId"]
            return lakehouse_id
        else:
            raise ValueError(f"Lakehouse name {target_lakehouse_name} not found in tenant scan")
        
    def getWorkspaceId(self, target_workspace_name):

        ws_lh_df = self.get_ws_lh_df()

        workspace_id_row = ws_lh_df.filter(ws_lh_df.workspaceName == target_workspace_name)\
                                .select("workspaceId").distinct()\
                                .collect()

        if workspace_id_row:
            workspace_id = workspace_id_row[0]["workspaceId"]
            return workspace_id
        else:
            raise ValueError(f"Workspace name {target_workspace_name} not found in tenant scan")

