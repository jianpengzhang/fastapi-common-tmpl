from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "example_group" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "name" VARCHAR(50) NOT NULL UNIQUE,
    "description" TEXT
);
COMMENT ON TABLE "example_group" IS '用例：用户组';
CREATE TABLE IF NOT EXISTS "example_user" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "username" VARCHAR(20) NOT NULL UNIQUE,
    "nickname" VARCHAR(50),
    "email" VARCHAR(255),
    "password" VARCHAR(128) NOT NULL,
    "last_login" TIMESTAMPTZ,
    "is_active" BOOL NOT NULL  DEFAULT True,
    "is_superuser" BOOL NOT NULL  DEFAULT False,
    "is_confirmed" BOOL NOT NULL  DEFAULT False,
    "avatar" VARCHAR(512),
    "group_id" BIGINT NOT NULL REFERENCES "example_group" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "example_user"."username" IS '用户名';
COMMENT ON COLUMN "example_user"."nickname" IS '昵称';
COMMENT ON COLUMN "example_user"."email" IS '联系邮箱';
COMMENT ON COLUMN "example_user"."password" IS '密码';
COMMENT ON COLUMN "example_user"."last_login" IS '上次登录';
COMMENT ON COLUMN "example_user"."is_active" IS '是否活跃';
COMMENT ON COLUMN "example_user"."is_superuser" IS '是否管理员';
COMMENT ON COLUMN "example_user"."is_confirmed" IS '是否确认';
COMMENT ON COLUMN "example_user"."avatar" IS '头像';
COMMENT ON TABLE "example_user" IS '用例：用户';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
