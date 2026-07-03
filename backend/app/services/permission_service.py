class PermissionService:
    def allowed_scopes_for_user(self, user_id: str) -> list[str]:
        raise NotImplementedError("Permission filtering is planned for phase 1.")
