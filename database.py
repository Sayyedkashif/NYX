
import motor.motor_asyncio
from datetime import datetime
import logging
from config import Config

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        self.movies = None
        self.users = None
        self.downloads = None

    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(Config.DATABASE_URI)
            self.db = self.client[Config.DATABASE_NAME]
            self.movies = self.db.movies
            self.users = self.db.users
            self.downloads = self.db.downloads

            # Test connection
            await self.client.admin.command('ping')
            logger.info("âœ… MangoDB connected successfully!")

            # Create indexes for better performance
            await self.create_indexes()

        except Exception as e:
            logger.error(f"âŒ MangoDB connection failed: {e}")
            raise

    async def create_indexes(self):
        """Create database indexes for faster queries"""
        try:
            # Movies collection indexes
            await self.movies.create_index("name")
            await self.movies.create_index("file_id")
            await self.movies.create_index("added_date")
            await self.movies.create_index("genre")

            # Users collection indexes  
            await self.users.create_index("user_id", unique=True)
            await self.users.create_index("join_date")

            # Downloads collection indexes
            await self.downloads.create_index("movie_id")
            await self.downloads.create_index("user_id")
            await self.downloads.create_index("download_date")

            logger.info("ðŸ“Š Database indexes created successfully!")

        except Exception as e:
            logger.error(f"Error creating indexes: {e}")

    async def add_user(self, user_id, username=None, first_name=None):
        """Add new user to database"""
        try:
            user_data = {
                "user_id": user_id,
                "username": username,
                "first_name": first_name,
                "join_date": datetime.now(),
                "is_active": True,
                "total_downloads": 0
            }

            await self.users.update_one(
                {"user_id": user_id},
                {"$setOnInsert": user_data},
                upsert=True
            )

        except Exception as e:
            logger.error(f"Error adding user: {e}")

    async def add_movie(self, movie_data):
        """Add new movie to database"""
        try:
            movie_doc = {
                "name": movie_data["name"],
                "file_id": movie_data["file_id"],
                "message_id": movie_data.get("message_id"),
                "file_type": movie_data["file_type"],
                "file_size": movie_data.get("file_size"),
                "year": movie_data.get("year"),
                "genre": movie_data.get("genre", "Movie"),
                "quality": movie_data.get("quality", "HD"),
                "rating": movie_data.get("rating"),
                "language": movie_data.get("language", "Hindi"),
                "added_by": movie_data["added_by"],
                "added_date": datetime.now(),
                "download_count": 0,
                "is_active": True
            }

            # Check if movie already exists
            existing = await self.movies.find_one({"file_id": movie_data["file_id"]})
            if existing:
                return False, "Movie already exists!"

            result = await self.movies.insert_one(movie_doc)
            return True, str(result.inserted_id)

        except Exception as e:
            logger.error(f"Error adding movie: {e}")
            return False, str(e)

    async def search_movies(self, query, limit=50):
        """Search movies in database"""
        try:
            # Create search regex (case insensitive)
            search_regex = {"$regex": query, "$options": "i"}

            # Search query
            search_filter = {
                "$and": [
                    {"is_active": True},
                    {
                        "$or": [
                            {"name": search_regex},
                            {"genre": search_regex},
                            {"language": search_regex}
                        ]
                    }
                ]
            }

            # Find movies with sorting
            cursor = self.movies.find(search_filter).sort("added_date", -1).limit(limit)
            movies = await cursor.to_list(length=limit)

            return movies

        except Exception as e:
            logger.error(f"Error searching movies: {e}")
            return []

    async def get_movie_by_id(self, movie_id):
        """Get movie by ID"""
        try:
            from bson import ObjectId
            movie = await self.movies.find_one({"_id": ObjectId(movie_id)})
            return movie
        except Exception as e:
            logger.error(f"Error getting movie by ID: {e}")
            return None

    async def update_download_count(self, movie_id):
        """Update movie download count"""
        try:
            from bson import ObjectId

            # Update movie download count
            await self.movies.update_one(
                {"_id": ObjectId(movie_id)},
                {"$inc": {"download_count": 1}}
            )

            # Add download record
            download_record = {
                "movie_id": movie_id,
                "download_date": datetime.now()
            }
            await self.downloads.insert_one(download_record)

        except Exception as e:
            logger.error(f"Error updating download count: {e}")

    async def get_stats(self):
        """Get bot statistics"""
        try:
            total_movies = await self.movies.count_documents({"is_active": True})
            total_users = await self.users.count_documents({"is_active": True})

            # Today's downloads
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_downloads = await self.downloads.count_documents({
                "download_date": {"$gte": today_start}
            })

            # Popular movies (top 5)
            popular_movies = await self.movies.find(
                {"is_active": True}
            ).sort("download_count", -1).limit(5).to_list(length=5)

            # Active channels count (approximate)
            active_channels = await self.movies.distinct("added_by")

            return {
                "total_movies": total_movies,
                "total_users": total_users,
                "today_downloads": today_downloads,
                "popular_movies": popular_movies,
                "active_channels": len(active_channels)
            }

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                "total_movies": 0,
                "total_users": 0,
                "today_downloads": 0,
                "popular_movies": [],
                "active_channels": 0
            }

    async def get_all_users(self):
        """Get all active users for broadcast"""
        try:
            cursor = self.users.find({"is_active": True}, {"user_id": 1})
            users = await cursor.to_list(length=None)
            return [user["user_id"] for user in users]
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []

    async def delete_movie(self, movie_id):
        """Delete movie (mark as inactive)"""
        try:
            from bson import ObjectId
            result = await self.movies.update_one(
                {"_id": ObjectId(movie_id)},
                {"$set": {"is_active": False}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error deleting movie: {e}")
            return False

    async def get_movies_by_genre(self, genre, limit=20):
        """Get movies by genre"""
        try:
            movies = await self.movies.find({
                "genre": {"$regex": genre, "$options": "i"},
                "is_active": True
            }).sort("added_date", -1).limit(limit).to_list(length=limit)

            return movies
        except Exception as e:
            logger.error(f"Error getting movies by genre: {e}")
            return []

    async def get_latest_movies(self, limit=10):
        """Get latest movies"""
        try:
            movies = await self.movies.find(
                {"is_active": True}
            ).sort("added_date", -1).limit(limit).to_list(length=limit)

            return movies
        except Exception as e:
            logger.error(f"Error getting latest movies: {e}")
            return []

    async def close_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("ðŸ”Œ MangoDB connection closed")
