import subprocess

from sqlalchemy import text


def check_database_access():
    """
    Ensure the database is accessible using `DATABASE_URL` from `.env`. If missing, set a default value that makes sense for your environment.
    """
    import asyncio
    from digest.config.settings import settings
    from sqlmodel import create_engine
        

    def get_docker_compose_command():
        commands = ["docker compose", "docker-compose"]

        for cmd in commands:
            try:
                subprocess.run(cmd.split(), check=True, text=True, capture_output=True)
                return cmd
            except subprocess.CalledProcessError:
                # Command not available
                continue
        return None
    async def test_connection():
        try:
            engine = create_engine(settings.DATABASE_URL)
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                print("✅ Successfully connected to the database.")
        except Exception:
            print(f"⚠️ Failed to connect to the database at `{settings.DATABASE_URL}`")
            docker_compose = get_docker_compose_command()

            if docker_compose:
                print(f"  ➡ Attempting to start the database using `{docker_compose} up -d postgres` (wait for it)")
                try:
                    subprocess.run(
                        [*docker_compose.split(), "up", "-d", "--wait", "postgres"],
                        check=True,
                        text=True,
                        capture_output=True,
                    )
                    print(f"  ✅ `{docker_compose} up -d postgres` executed successfully. Retrying connection...")
                    # Retry the database connection after starting the container
                    engine = create_engine(settings.DATABASE_URL)
                    with engine.connect() as connection:
                        connection.execute(text("SELECT 1"))
                        print("  ✅ Successfully connected to the database after starting the container.")
                except subprocess.CalledProcessError as docker_error:
                    print(f"  ❌ Failed to start the database using `{docker_compose} up -d postgres`:\n  {docker_error}")
                except Exception as retry_error:
                    print(f"  ❌ Retried database connection but failed again:\n  {retry_error}")
            else:
                print("  ❌ Docker Compose is not available, so not able to start db automatically.")

    asyncio.run(test_connection())


def prepare():
    check_database_access()