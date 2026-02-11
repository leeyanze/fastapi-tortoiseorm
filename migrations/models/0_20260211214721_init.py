from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "team" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS "tournament" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" TEXT NOT NULL,
    "created" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "event" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" TEXT NOT NULL,
    "modified" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "prize" VARCHAR(40),
    "tournament_id" INT NOT NULL REFERENCES "tournament" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);
CREATE TABLE IF NOT EXISTS "event_team" (
    "event_id" INT NOT NULL REFERENCES "event" ("id") ON DELETE CASCADE,
    "team_id" INT NOT NULL REFERENCES "team" ("id") ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS "uidx_event_team_event_i_5cea5b" ON "event_team" ("event_id", "team_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "eJztWFtP2zAU/itVn0DqUOkKQ3sLbRkdtJ0g2xAIRSYxqUViB8cBOtT/PtuJ49wIZdyK1h"
    "dIz8U+5zvX5L7pEwd64cbgBmLW/Nq4b2LgQ/6QZ7QaTRAEmiwIDFx4UhKmIhcho8AW51wC"
    "L4Sc5MDQpihgiGBOxZHnCSKxuSDCriZFGF1H0GLEhWwKKWecnXMywg68g6H6GVxZlwh6Ts"
    "5Q5Ii7Jd1is0DShpjtSUFx24VlEy/ysRYOZmxKcCqNYvNdiCEFDIrjGY2E+cK6xE3lUWyp"
    "FolNzOg48BJEHsu4uyAGNsECP25NKB10xS2fOpvdL92dz9vdHS4iLUkpX+axe9r3WFEiMD"
    "abc8kHDMQSEkaNm/xfQs6Edw9Ap+QL4HGTi+ApqOrQUwQNn06Zl8GvBhxzcGIKo/0wvPYE"
    "YfzLOOrtG0drI+NkXXJmCedwMv6mxAlP7jjlx73Dya7EN1cwiF9WkY19jgtDPqzGNatXwN"
    "ZJFDfUw3Ii3aQQOBPszZIiqEN+OBocm8boRw7+vmEOBKeTg15R17bX8+inhzR+D839hvjZ"
    "OJ2MBxJBEjKXyhu1nHnaFDaBiBELk1sLOJl6VVRtvI5pQNGfiiLpQxv5wKuOZ6pTDGastJ"
    "EoLxDKxMDlqJn+oDccGYdrm+1WR8aDRwkx6Zkqnm57vVATjERUPGNmPalNl/Qe79hLUgov"
    "0LTFpLu8quzZGpcymHuEQuTiAziTmA65XQDbVZmYjHYzd9jyYTlXWaGouiQouE03gXKycF"
    "e5gzBOzp5x3DP6g6aE9QLYV7eAOlYOX8EhHVKgpLJllt/xK8MTAMqQjQIgPCgFaATwzCTi"
    "76IBgsD/l9C89mZSExhpuVXYIZUfFHrCi5QtF8cYKEIl1FdwJiPKFZJYplFIWFIn4bEpJZ"
    "E71WSWXFSZAJxulZCUWeEDDFxJE/7OW3nDK5Zi5dDDO7GyZLUSL1t3Xa3Er7sSl6bXG/Td"
    "TCN5XsdN33Y/estNHSn23NKIynfebHsttt5MV35e55Vrdn3j1atJVfvNLS41TTgvt2rFq1"
    "b8X7Xi7JuYzd/R2dM/TmTUVt8m3vXbhF5XF5yuj4/H3URv7+BITAmB7MtPxvd7T5w/c7+o"
    "nVAGpMieVk2nhFM7mYCWWU2lDzSVbiANkzLJg9ebAlqNXkblo8wmnvV3lgexy0SCd7a2aj"
    "BTo4lLFTqhmlqdmJcfR6I0ngBiIv4xAdxstxcAkEs9CKDkFeY5wazyM+D348n4gVmuVQpA"
    "/sTcwTMH2azV8FDIzpcT1hoUhdf1O1NxPSrMY3HA276+VoyX+V/1WINs"
)
