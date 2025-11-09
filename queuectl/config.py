from queuectl.db import db


DEFAULT_CONFIG = {
    "max_retries": 3,
    "backoff_base": 2,
}


def get_config(key: str, default=None):
    """Fetch a configuration value from the database or defaults."""
    doc = db.config.find_one({"_id": key})
    if doc:
        return doc["value"]
    return DEFAULT_CONFIG.get(key, default)


def set_config(key: str, value):
    """Set or update a configuration value."""
    db.config.update_one(
        {"_id": key},
        {"$set": {"value": value}},
        upsert=True
    )


def get_all_config():
    """Return all configuration key-value pairs."""
    configs = DEFAULT_CONFIG.copy()
    for entry in db.config.find():
        configs[entry["_id"]] = entry["value"]
    return configs
