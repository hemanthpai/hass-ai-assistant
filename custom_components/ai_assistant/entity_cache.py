"""Cache the exposed entities to enable validation of entity IDs in the instructor tools."""



class EntityCache:
    """Cache the exposed entities to enable validation of entity IDs in the instructor tools."""

    _instance = None

    def __init__(self, entities: list[dict]) -> None:
        """Initialize the EntityCache."""
        self._entities: list[dict] = entities

    @staticmethod
    def get_instance() -> "EntityCache":
        """Get the EntityCache instance."""
        if EntityCache._instance is None:
            raise ValueError("EntityCache hasn't been initialized yet.")
        return EntityCache._instance

    @staticmethod
    def create_instance(entities: list[dict]):
        """Create a new EntityCache instance."""
        EntityCache._instance = EntityCache(entities)

    def is_exposed_entity(self, entity_id: str, domain: str) -> bool:
        """Check if an entity is exposed."""
        if "group_by_domain" in self._entities:
            if domain in self._entities["group_by_domain"]:
                return any(
                    entity["entity_id"] == entity_id
                    for entity in self._entities["group_by_domain"][domain]
                )
        return False
