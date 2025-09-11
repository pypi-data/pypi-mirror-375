from azure_datastore_utils import CosmosDBUtils


def get_all_purchases():
    client = CosmosDBUtils(database_name="retailstore", collection="purchases", auth_strategy='ConnectionString')

    all_items = client.get_all_items()
    print(all_items)


def get_single_purchase():
    client = CosmosDBUtils(database_name="retailstore", collection="purchases", auth_strategy='ConnectionString')
    receipt_id: str = "100001"
    customer_id: str = "jacob@contosogroceries.ai"

    single_purchase = client.get_single_item(item_id=receipt_id, partition_key=customer_id)
    print(single_purchase)



# uv run -m tests.test_cosmos_db

if __name__ == "__main__":
    get_single_purchase()