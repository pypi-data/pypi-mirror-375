import json
import os
import re
import ssl
import subprocess
import uuid
from datetime import datetime, timezone
from typing import Union, List, Dict, Optional, Any

import logging
from dotenv import load_dotenv

from .context import Context
from pymongo import MongoClient

from .database import db_connection
from .utils import create_response, mqtt_publish, _format_duration
from .todo_log_service import log_todo_create, log_todo_update, log_todo_delete, log_todo_complete

# Load environment variables
load_dotenv()

# Get the logger
logger = logging.getLogger(__name__)

# Cache constants
TAGS_CACHE_KEY = "all_lesson_tags"
TAGS_CACHE_EXPIRY = 43200  # Cache expiry in seconds (12 hours)
PROJECTS_CACHE_KEY = "all_valid_projects"
PROJECTS_CACHE_EXPIRY = 43200  # Cache expiry in seconds (12 hours)

# Valid project list - all lowercase for case-insensitive matching
# TODO: This will be migrated to MongoDB and deprecated
VALID_PROJECTS = [
    "madness_interactive", "regressiontestkit", "omnispindle",
    "todomill_projectorium", "swarmonomicon", "hammerspoon",

    "lab_management", "cogwyrm", "docker_implementation",
    "documentation", "eventghost-rust", "hammerghost",
    "quality_assurance", "spindlewrit", "inventorium"
]

# Cache utility functions
def cache_lesson_tags(tags_list, ctx=None):
    """
    Cache the list of all lesson tags in MongoDB.
    
    Args:
        tags_list: List of tags to cache
        ctx: Optional context for user-scoped collections
    """
    try:
        # Get user-scoped collections
        collections = db_connection.get_collections(ctx.user if ctx else None)
        tags_cache_collection = collections['tags_cache']
        
        # Add timestamp for cache expiry management
        cache_entry = {
            "key": TAGS_CACHE_KEY,
            "tags": list(tags_list),
            "updated_at": int(datetime.now(timezone.utc).timestamp())
        }

        # Use upsert to update if exists or insert if not
        tags_cache_collection.update_one(
            {"key": TAGS_CACHE_KEY},
            {"$set": cache_entry},
            upsert=True
        )
        return True
    except Exception as e:
        logging.error(f"Failed to cache lesson tags: {str(e)}")
        return False

def get_cached_lesson_tags(ctx=None):
    """
    Retrieve the cached list of lesson tags from MongoDB.
    
    Args:
        ctx: Optional context for user-scoped collections
    
    Returns:
        List of tags if cache exists and is valid, None otherwise
    """
    try:
        # Get user-scoped collections
        collections = db_connection.get_collections(ctx.user if ctx else None)
        tags_cache_collection = collections['tags_cache']
        
        # Find the cache entry
        cache_entry = tags_cache_collection.find_one({"key": TAGS_CACHE_KEY})

        if not cache_entry:
            return None

        # Check if cache is expired
        current_time = int(datetime.now(timezone.utc).timestamp())
        if current_time - cache_entry["updated_at"] > TAGS_CACHE_EXPIRY:
            # Cache expired, invalidate it
            invalidate_lesson_tags_cache(ctx)
            return None

        return cache_entry["tags"]
    except Exception as e:
        logging.error(f"Failed to retrieve cached lesson tags: {str(e)}")
        return None

def invalidate_lesson_tags_cache(ctx=None):
    """
    Invalidate the lesson tags cache in MongoDB.
    
    Args:
        ctx: Optional context for user-scoped collections
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get user-scoped collections
        collections = db_connection.get_collections(ctx.user if ctx else None)
        tags_cache_collection = collections['tags_cache']
        
        tags_cache_collection.delete_one({"key": TAGS_CACHE_KEY})
        return True
    except Exception as e:
        logging.error(f"Failed to invalidate lesson tags cache: {str(e)}")
        return False

def get_all_lesson_tags(ctx=None):
    """
    Get all unique tags from lessons, with caching.
    
    First tries to fetch from cache, falls back to database if needed.
    Also updates the cache if fetching from database.
    
    Args:
        ctx: Optional context for user-scoped collections
    
    Returns:
        List of all unique tags
    """
    cached_tags = get_cached_lesson_tags(ctx)
    if cached_tags is not None:
        return cached_tags

    # If not in cache, query from database
    try:
        # Get user-scoped collections
        collections = db_connection.get_collections(ctx.user if ctx else None)
        lessons_collection = collections['lessons']
        
        # Use MongoDB aggregation to get all unique tags
        pipeline = [
            {"$project": {"tags": 1}},
            {"$unwind": "$tags"},
            {"$group": {"_id": None, "unique_tags": {"$addToSet": "$tags"}}},
        ]
        result = list(lessons_collection.aggregate(pipeline))

        # Extract tags from result
        all_tags = []
        if result and 'unique_tags' in result[0]:
            all_tags = result[0]['unique_tags']

        # Cache the results for future use
        cache_lesson_tags(all_tags, ctx)
        return all_tags
    except Exception as e:
        logging.error(f"Failed to aggregate lesson tags: {str(e)}")
        return []

# Project management functions
def cache_projects(projects_list, ctx=None):
    """
    Cache the list of valid projects in MongoDB.
    
    Args:
        projects_list: List of project names to cache
        ctx: Optional context for user-scoped collections
    """
    try:
        # Get user-scoped collections
        collections = db_connection.get_collections(ctx.user if ctx else None)
        tags_cache_collection = collections['tags_cache']
        
        cache_entry = {
            "key": PROJECTS_CACHE_KEY,
            "projects": list(projects_list),
            "updated_at": int(datetime.now(timezone.utc).timestamp())
        }
        tags_cache_collection.update_one(
            {"key": PROJECTS_CACHE_KEY},
            {"$set": cache_entry},
            upsert=True
        )
        return True
    except Exception as e:
        logging.error(f"Failed to cache projects: {str(e)}")
        return False

def get_cached_projects(ctx=None):
    """
    Retrieve the cached list of valid projects from MongoDB.
    
    Args:
        ctx: Optional context for user-scoped collections
    
    Returns:
        List of project names if cache exists and is valid, None otherwise
    """
    try:
        # Get user-scoped collections
        collections = db_connection.get_collections(ctx.user if ctx else None)
        tags_cache_collection = collections['tags_cache']
        
        cache_entry = tags_cache_collection.find_one({"key": PROJECTS_CACHE_KEY})

        if not cache_entry:
            return None

        # Check if cache is expired
        current_time = int(datetime.now(timezone.utc).timestamp())
        if current_time - cache_entry["updated_at"] > PROJECTS_CACHE_EXPIRY:
            invalidate_projects_cache(ctx)
            return None

        return cache_entry["projects"]
    except Exception as e:
        logging.error(f"Failed to retrieve cached projects: {str(e)}")
        return None

def invalidate_projects_cache(ctx=None):
    """
    Invalidate the projects cache in MongoDB.
    
    Args:
        ctx: Optional context for user-scoped collections
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get user-scoped collections
        collections = db_connection.get_collections(ctx.user if ctx else None)
        tags_cache_collection = collections['tags_cache']
        
        tags_cache_collection.delete_one({"key": PROJECTS_CACHE_KEY})
        return True
    except Exception as e:
        logging.error(f"Failed to invalidate projects cache: {str(e)}")
        return False

def initialize_projects_collection(ctx=None):
    """
    Initialize the projects collection with the current VALID_PROJECTS list.
    This is a one-time migration function that includes git URLs and paths.
    
    Args:
        ctx: Optional context for user-scoped collections
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get user-scoped collections
        collections = db_connection.get_collections(ctx.user if ctx else None)
        projects_collection = collections['projects']
        
        # Check if projects collection is already populated
        existing_count = projects_collection.count_documents({})
        if existing_count > 0:
            logging.info(f"Projects collection already has {existing_count} projects")
            return True

        # Insert all valid projects with enhanced metadata
        current_time = int(datetime.now(timezone.utc).timestamp())
        project_definitions = {
            "madness_interactive": {
                "git_url": "https://github.com/d-edens/madness_interactive.git",
                "relative_path": "",
                "description": "Main Madness Interactive project hub"
            },
            "regressiontestkit": {
                "git_url": "https://github.com/d-edens/RegressionTestKit.git",
                "relative_path": "../RegressionTestKit",
                "description": "A toolkit for regression testing"
            }
        }
        projects_to_insert = [
            {
                "id": name,
                "name": name,
                "display_name": name.replace("_", " ").title(),
                "created_at": current_time,
                **project_definitions.get(name, {})
            }
            for name in VALID_PROJECTS
        ]

        if projects_to_insert:
            projects_collection.insert_many(projects_to_insert)
            logging.info(f"Successfully inserted {len(projects_to_insert)} projects into the collection")

        # Invalidate project cache after initialization
        invalidate_projects_cache(ctx)
        return True

    except Exception as e:
        logging.error(f"Failed to initialize projects collection: {str(e)}")
        return False

def get_all_projects(ctx=None):
    """
    Get all projects from the database, with caching.
    
    Args:
        ctx: Optional context for user-scoped collections
    """
    cached_projects = get_cached_projects(ctx)
    if cached_projects:
        return cached_projects

    try:
        # Get user-scoped collections
        collections = db_connection.get_collections(ctx.user if ctx else None)
        projects_collection = collections['projects']
        
        # Get all projects from the database
        projects_from_db = list(projects_collection.find({}, {"_id": 0}))

        # If the database is empty, initialize it as a fallback
        if not projects_from_db:
            initialize_projects_collection(ctx)
            projects_from_db = list(projects_collection.find({}, {"_id": 0}))

        # Cache the results for future use
        cache_projects(projects_from_db, ctx)
        return projects_from_db
    except Exception as e:
        logging.error(f"Failed to get projects from database: {str(e)}")
        return []

def validate_project_name(project: str) -> str:
    # Normalize project name for validation
    project_lower = project.lower()

    # Check if the normalized project name is in the list of valid projects
    if project_lower in [p.lower() for p in VALID_PROJECTS]:
        return project_lower  # Return the lowercase version for consistency

    # Default to "madness_interactive" if not found
    return "madness_interactive"

async def add_todo(description: str, project: str, priority: str = "Medium", target_agent: str = "user", metadata: Optional[Dict[str, Any]] = None, ctx: Optional[Context] = None) -> str:
    """
    Creates a task in the specified project with the given priority and target agent.
    Returns a compact representation of the created todo with an ID for reference.
    """
    todo_id = str(uuid.uuid4())
    validated_project = validate_project_name(project)
    todo = {
        "id": todo_id,
        "description": description,
        "project": validated_project,
        "priority": priority,
        "status": "pending",
        "target_agent": target_agent,
        "created_at": int(datetime.now(timezone.utc).timestamp()),
        "metadata": metadata or {}
    }
    try:
        # Get user-scoped collections
        collections = db_connection.get_collections(ctx.user if ctx else None)
        todos_collection = collections['todos']
        
        todos_collection.insert_one(todo)
        user_email = ctx.user.get("email", "anonymous") if ctx and ctx.user else "anonymous"
        logger.info(f"Todo created by {user_email} in user database: {todo_id}")
        await log_todo_create(todo_id, description, project, user_email)

        # Get project todo counts from user's database
        pipeline = [
            {"$match": {"project": validated_project}},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        counts = list(todos_collection.aggregate(pipeline))
        project_counts = {
            "pending": 0,
            "completed": 0,
        }
        for status_count in counts:
            if status_count["_id"] in project_counts:
                project_counts[status_count["_id"]] = status_count["count"]

        return create_response(True,
            {
                "operation": "create",
                "status": "success",
                "todo_id": todo_id,
                "description": description[:40] + ("..." if len(description) > 40 else ""),
                "project_counts": project_counts
            },
            message=f"Todo '{description[:30]}...' created in '{validated_project}'. Pending: {project_counts['pending']}, Completed: {project_counts['completed']}."
        )
    except Exception as e:
        logger.error(f"Failed to create todo: {str(e)}")
        return create_response(False, message=str(e))

async def query_todos(filter: Optional[Dict[str, Any]] = None, projection: Optional[Dict[str, Any]] = None, limit: int = 100, ctx: Optional[Context] = None) -> str:
    """
    Query todos with flexible filtering options from user's database.
    """
    try:
        # Get user-scoped collections
        collections = db_connection.get_collections(ctx.user if ctx else None)
        todos_collection = collections['todos']
        
        cursor = todos_collection.find(filter or {}, projection).limit(limit)
        results = list(cursor)
        return create_response(True, {"items": results})
    except Exception as e:
        logger.error(f"Failed to query todos: {str(e)}")
        return create_response(False, message=str(e))

async def update_todo(todo_id: str, updates: dict, ctx: Optional[Context] = None) -> str:
    """
    Update a todo with the provided changes.
    """
    if "updated_at" not in updates:
        updates["updated_at"] = int(datetime.now(timezone.utc).timestamp())
    try:
        # Get user-scoped collections
        collections = db_connection.get_collections(ctx.user if ctx else None)
        todos_collection = collections['todos']
        
        existing_todo = todos_collection.find_one({"id": todo_id})
        if not existing_todo:
            return create_response(False, message=f"Todo {todo_id} not found.")

        result = todos_collection.update_one({"id": todo_id}, {"$set": updates})
        if result.modified_count == 1:
            user_email = ctx.user.get("email", "anonymous") if ctx and ctx.user else "anonymous"
            logger.info(f"Todo updated by {user_email}: {todo_id}")
            description = updates.get('description', existing_todo.get('description', 'Unknown'))
            project = updates.get('project', existing_todo.get('project', 'Unknown'))
            changes = [
                {"field": field, "old_value": existing_todo.get(field), "new_value": value}
                for field, value in updates.items()
                if field != 'updated_at' and existing_todo.get(field) != value
            ]
            await log_todo_update(todo_id, description, project, changes, user_email)
            return create_response(True, message=f"Todo {todo_id} updated successfully")
        else:
            return create_response(False, message=f"Todo {todo_id} not found or no changes made.")
    except Exception as e:
        logger.error(f"Failed to update todo: {str(e)}")
        return create_response(False, message=str(e))

async def delete_todo(todo_id: str, ctx: Optional[Context] = None) -> str:
    """
    Delete a todo item by its ID.
    """
    try:
        # Get user-scoped collections
        collections = db_connection.get_collections(ctx.user if ctx else None)
        todos_collection = collections['todos']
        
        existing_todo = todos_collection.find_one({"id": todo_id})
        if existing_todo:
            user_email = ctx.user.get("email", "anonymous") if ctx and ctx.user else "anonymous"
            logger.info(f"Todo deleted by {user_email}: {todo_id}")
            await log_todo_delete(todo_id, existing_todo.get('description', 'Unknown'),
                                  existing_todo.get('project', 'Unknown'), user_email)
        result = todos_collection.delete_one({"id": todo_id})
        if result.deleted_count == 1:
            return create_response(True, message=f"Todo {todo_id} deleted successfully.")
        else:
            return create_response(False, message=f"Todo {todo_id} not found.")
    except Exception as e:
        logger.error(f"Failed to delete todo: {str(e)}")
        return create_response(False, message=str(e))

async def get_todo(todo_id: str, ctx: Optional[Context] = None) -> str:
    """
    Get a specific todo item by its ID.
    """
    try:
        # Get user-scoped collections
        collections = db_connection.get_collections(ctx.user if ctx else None)
        todos_collection = collections['todos']
        
        todo = todos_collection.find_one({"id": todo_id})
        if todo:
            return create_response(True, todo)
        else:
            return create_response(False, message=f"Todo with ID {todo_id} not found.")
    except Exception as e:
        logger.error(f"Failed to get todo: {str(e)}")
        return create_response(False, message=str(e))

async def mark_todo_complete(todo_id: str, comment: Optional[str] = None, ctx: Optional[Context] = None) -> str:
    """
    Mark a todo as completed.
    """
    try:
        # Get user-scoped collections
        collections = db_connection.get_collections(ctx.user if ctx else None)
        todos_collection = collections['todos']
        
        existing_todo = todos_collection.find_one({"id": todo_id})
        if not existing_todo:
            return create_response(False, message=f"Todo {todo_id} not found.")

        completed_at = int(datetime.now(timezone.utc).timestamp())
        duration_sec = completed_at - existing_todo.get('created_at', completed_at)
        updates = {
            "status": "completed",
            "completed_at": completed_at,
            "duration": _format_duration(duration_sec),
            "duration_sec": duration_sec,
            "updated_at": completed_at
        }
        if comment:
            updates["metadata.completion_comment"] = comment
            user_email = ctx.user.get("email", "anonymous") if ctx and ctx.user else "anonymous"
            updates["metadata.completed_by"] = user_email

        result = todos_collection.update_one({"id": todo_id}, {"$set": updates})
        if result.modified_count == 1:
            user_email = ctx.user.get("email", "anonymous") if ctx and ctx.user else "anonymous"
            logger.info(f"Todo completed by {user_email}: {todo_id}")
            await log_todo_complete(todo_id, existing_todo.get('description', 'Unknown'),
                                    existing_todo.get('project', 'Unknown'), user_email)
            return create_response(True, message=f"Todo {todo_id} marked as complete.")
        else:
            return create_response(False, message=f"Failed to update todo {todo_id}.")
    except Exception as e:
        logger.error(f"Failed to mark todo complete: {str(e)}")
        return create_response(False, message=str(e))


async def list_todos_by_status(status: str, limit: int = 100, ctx: Optional[Context] = None) -> str:
    """
    List todos filtered by their status.
    """
    if status.lower() not in ['pending', 'completed', 'initial']:
        return create_response(False, message="Invalid status. Must be one of 'pending', 'completed', 'initial'.")
    return await query_todos(filter={"status": status.lower()}, limit=limit, ctx=ctx)

async def add_lesson(language: str, topic: str, lesson_learned: str, tags: Optional[list] = None, ctx: Optional[Context] = None) -> str:
    """
    Add a new lesson to the knowledge base.
    """
    lesson = {
        "id": str(uuid.uuid4()),
        "language": language,
        "topic": topic,
        "lesson_learned": lesson_learned,
        "tags": tags or [],
        "created_at": int(datetime.now(timezone.utc).timestamp())
    }
    try:
        # Get user-scoped collections
        collections = db_connection.get_collections(ctx.user if ctx else None)
        lessons_collection = collections['lessons']
        
        lessons_collection.insert_one(lesson)
        if tags:
            # Invalidate the tags cache when new tags are added
            invalidate_lesson_tags_cache(ctx)
        return create_response(True, lesson)
    except Exception as e:
        logger.error(f"Failed to add lesson: {str(e)}")
        return create_response(False, message=str(e))

async def get_lesson(lesson_id: str, ctx: Optional[Context] = None) -> str:
    """
    Get a specific lesson by its ID.
    """
    try:
        # Get user-scoped collections
        collections = db_connection.get_collections(ctx.user if ctx else None)
        lessons_collection = collections['lessons']
        
        lesson = lessons_collection.find_one({"id": lesson_id})
        if lesson:
            return create_response(True, lesson)
        else:
            return create_response(False, message=f"Lesson with ID {lesson_id} not found.")
    except Exception as e:
        logger.error(f"Failed to get lesson: {str(e)}")
        return create_response(False, message=str(e))

async def update_lesson(lesson_id: str, updates: dict, ctx: Optional[Context] = None) -> str:
    """
    Update an existing lesson.
    """
    try:
        # Get user-scoped collections
        collections = db_connection.get_collections(ctx.user if ctx else None)
        lessons_collection = collections['lessons']
        
        result = lessons_collection.update_one({"id": lesson_id}, {"$set": updates})
        if result.modified_count == 1:
            if 'tags' in updates:
                # Invalidate the tags cache when tags are modified
                invalidate_lesson_tags_cache(ctx)
            return create_response(True, message=f"Lesson {lesson_id} updated.")
        else:
            return create_response(False, message=f"Lesson {lesson_id} not found.")
    except Exception as e:
        logger.error(f"Failed to update lesson: {str(e)}")
        return create_response(False, message=str(e))

async def delete_lesson(lesson_id: str, ctx: Optional[Context] = None) -> str:
    """
    Delete a lesson by its ID.
    """
    try:
        # Get user-scoped collections
        collections = db_connection.get_collections(ctx.user if ctx else None)
        lessons_collection = collections['lessons']
        
        result = lessons_collection.delete_one({"id": lesson_id})
        if result.deleted_count == 1:
            # Invalidate the tags cache when lessons are deleted
            invalidate_lesson_tags_cache(ctx)
            return create_response(True, message=f"Lesson {lesson_id} deleted.")
        else:
            return create_response(False, message=f"Lesson {lesson_id} not found.")
    except Exception as e:
        logger.error(f"Failed to delete lesson: {str(e)}")
        return create_response(False, message=str(e))

async def search_todos(query: str, fields: Optional[list] = None, limit: int = 100, ctx: Optional[Context] = None) -> str:
    """
    Search todos with text search capabilities.
    """
    if fields is None:
        fields = ["description", "project"]
    search_query = {
        "$or": [{field: {"$regex": query, "$options": "i"}} for field in fields]
    }
    return await query_todos(filter=search_query, limit=limit, ctx=ctx)

async def grep_lessons(pattern: str, limit: int = 20, ctx: Optional[Context] = None) -> str:
    """
    Search lessons with grep-style pattern matching across topic and content.
    """
    try:
        # Get user-scoped collections
        collections = db_connection.get_collections(ctx.user if ctx else None)
        lessons_collection = collections['lessons']
        
        search_query = {
            "$or": [
                {"topic": {"$regex": pattern, "$options": "i"}},
                {"lesson_learned": {"$regex": pattern, "$options": "i"}}
            ]
        }
        cursor = lessons_collection.find(search_query).limit(limit)
        results = list(cursor)
        return create_response(True, {"items": results})
    except Exception as e:
        logger.error(f"Failed to grep lessons: {str(e)}")
        return create_response(False, message=str(e))

async def list_project_todos(project: str, limit: int = 5, ctx: Optional[Context] = None) -> str:
    """
    List recent active todos for a specific project.
    """
    return await query_todos(
        filter={"project": project.lower(), "status": "pending"},
        limit=limit,
        ctx=ctx
    )

async def query_todo_logs(filter_type: str = 'all', project: str = 'all',
                       page: int = 1, page_size: int = 20, ctx: Optional[Context] = None) -> str:
    """
    Query the todo logs with filtering and pagination.
    """
    from .todo_log_service import get_service_instance
    service = get_service_instance()
    logs = await service.get_logs(filter_type, project, page, page_size)
    return create_response(True, logs)

async def list_projects(include_details: Union[bool, str] = False, madness_root: str = "/Users/d.edens/lab/madness_interactive", ctx: Optional[Context] = None) -> str:
    """
    List all valid projects from the centralized project management system.
    """
    # This tool now directly returns the hardcoded list of valid projects
    return create_response(True, {"projects": VALID_PROJECTS})

async def add_explanation(topic: str, content: str, kind: str = "concept", author: str = "system", ctx: Optional[Context] = None) -> str:
    """
    Add a new explanation to the knowledge base.
    """
    explanation = {
        "topic": topic,
        "content": content,
        "kind": kind,
        "author": author,
        "created_at": datetime.now(timezone.utc)
    }
    try:
        # Get user-scoped collections
        collections = db_connection.get_collections(ctx.user if ctx else None)
        explanations_collection = collections['explanations']
        
        explanations_collection.update_one(
            {"topic": topic},
            {"$set": explanation},
            upsert=True
        )
        return create_response(True, explanation, f"Explanation for '{topic}' added/updated.")
    except Exception as e:
        logger.error(f"Failed to add explanation: {str(e)}")
        return create_response(False, message=str(e))

async def get_explanation(topic: str, ctx: Optional[Context] = None) -> str:
    """Get an explanation for a given topic."""
    try:
        # Get user-scoped collections
        collections = db_connection.get_collections(ctx.user if ctx else None)
        explanations_collection = collections['explanations']
        
        explanation = explanations_collection.find_one({"topic": topic})
        if explanation:
            return create_response(True, explanation)
        return create_response(False, message=f"Explanation for '{topic}' not found.")
    except Exception as e:
        logger.error(f"Failed to get explanation: {str(e)}")
        return create_response(False, message=str(e))

async def update_explanation(topic: str, updates: dict, ctx: Optional[Context] = None) -> str:
    """Update an existing explanation."""
    try:
        # Get user-scoped collections
        collections = db_connection.get_collections(ctx.user if ctx else None)
        explanations_collection = collections['explanations']
        
        result = explanations_collection.update_one({"topic": topic}, {"$set": updates})
        if result.modified_count:
            return create_response(True, message="Explanation updated.")
        return create_response(False, message="Explanation not found or no changes made.")
    except Exception as e:
        logger.error(f"Failed to update explanation: {str(e)}")
        return create_response(False, message=str(e))

async def delete_explanation(topic: str, ctx: Optional[Context] = None) -> str:
    """Delete an explanation for a given topic."""
    try:
        # Get user-scoped collections
        collections = db_connection.get_collections(ctx.user if ctx else None)
        explanations_collection = collections['explanations']
        
        result = explanations_collection.delete_one({"topic": topic})
        if result.deleted_count:
            return create_response(True, message="Explanation deleted.")
        return create_response(False, message="Explanation not found.")
    except Exception as e:
        logger.error(f"Failed to delete explanation: {str(e)}")
        return create_response(False, message=str(e))


async def explain_tool(topic: str, brief: bool = False, ctx: Optional[Context] = None) -> str:
    """
    Provides a detailed explanation for a project or concept.
    """
    from . import explain as explain_module
    explanation = await explain_module.explain(topic, brief)
    return create_response(True, {"topic": topic, "explanation": explanation})


async def list_lessons(limit: int = 100, brief: bool = False, ctx: Optional[Context] = None) -> str:
    """
    List all lessons, sorted by creation date.
    """
    try:
        # Get user-scoped collections
        collections = db_connection.get_collections(ctx.user if ctx else None)
        lessons_collection = collections['lessons']
        
        cursor = lessons_collection.find().sort("created_at", -1).limit(limit)
        results = list(cursor)
        if brief:
            results = [{"id": r["id"], "topic": r["topic"], "language": r["language"]} for r in results]
        return create_response(True, {"items": results})
    except Exception as e:
        logger.error(f"Failed to list lessons: {str(e)}")
        return create_response(False, message=str(e))

async def search_lessons(query: str, fields: Optional[list] = None, limit: int = 100, brief: bool = False, ctx: Optional[Context] = None) -> str:
    """
    Search lessons with text search capabilities.
    """
    if fields is None:
        fields = ["topic", "lesson_learned", "tags"]
    search_query = {
        "$or": [{field: {"$regex": query, "$options": "i"}} for field in fields]
    }
    try:
        # Get user-scoped collections
        collections = db_connection.get_collections(ctx.user if ctx else None)
        lessons_collection = collections['lessons']
        
        cursor = lessons_collection.find(search_query).limit(limit)
        results = list(cursor)
        if brief:
            results = [{"id": r["id"], "topic": r["topic"], "language": r["language"]} for r in results]
        return create_response(True, {"items": results})
    except Exception as e:
        logger.error(f"Failed to search lessons: {str(e)}")
        return create_response(False, message=str(e))


async def point_out_obvious(observation: str, sarcasm_level: int = 5, ctx: Optional[Context] = None) -> str:
    """
    Points out something obvious to the human user with varying levels of humor.
    
    Args:
        observation: The obvious thing to point out
        sarcasm_level: Scale from 1-10 (1=gentle, 10=maximum sass)
        ctx: Optional context
    
    Returns:
        A response highlighting the obvious with appropriate commentary
    """
    import random
    
    # Sarcasm templates based on level
    templates = {
        1: ["Just a friendly observation: {obs}", "I noticed that {obs}"],
        2: ["It seems that {obs}", "Apparently, {obs}"],
        3: ["Fun fact: {obs}", "Did you know? {obs}"],
        4: ["Breaking news: {obs}", "Alert: {obs}"],
        5: ["Captain Obvious reporting: {obs}", "In today's episode of 'Things We Already Know': {obs}"],
        6: ["🎉 Congratulations! You've discovered that {obs}", "Achievement unlocked: Noticing that {obs}"],
        7: ["*drum roll* ... {obs}", "Stop the presses! {obs}"],
        8: ["I'm sure you're shocked to learn that {obs}", "Brace yourself: {obs}"],
        9: ["In other groundbreaking revelations: {obs}", "Nobel Prize committee, take note: {obs}"],
        10: ["🤯 Mind = Blown: {obs}", "Call the scientists, we've confirmed that {obs}"]
    }
    
    # Clamp sarcasm level
    level = max(1, min(10, sarcasm_level))
    
    # Pick a random template for the level
    template_options = templates.get(level, templates[5])
    template = random.choice(template_options)
    
    # Format the response
    response = template.format(obs=observation)
    
    # Add emoji based on level
    if level >= 7:
        emojis = ["🙄", "😏", "🤔", "🧐", "🎭"]
        response = f"{random.choice(emojis)} {response}"
    
    # Log the obvious observation (for science)
    logger.info(f"Obvious observation made (sarcasm={level}): {observation}")
    
    # Store in a special "obvious_things" collection if we have DB
    try:
        # Get user-scoped collections - use a generic collection access
        collections = db_connection.get_collections(ctx.user if ctx else None)
        # Access the database directly for custom collections like obvious_observations
        obvious_collection = collections.database["obvious_observations"]
        obvious_collection.insert_one({
            "observation": observation,
            "sarcasm_level": level,
            "timestamp": datetime.now(timezone.utc),
            "user": ctx.user.get("sub") if ctx and ctx.user else "anonymous",
            "response": response
        })
    except Exception as e:
        logger.debug(f"Failed to store obvious observation: {e}")
    
    # Publish to MQTT for other systems to enjoy the obviousness
    try:
        mqtt_publish("observations/obvious", {
            "observation": observation,
            "sarcasm_level": level,
            "response": response
        })
    except Exception as e:
        logger.debug(f"Failed to publish obvious observation: {e}")
    
    return create_response(True, {
        "response": response,
        "observation": observation,
        "sarcasm_level": level,
        "meta": {
            "obviousness_score": min(100, level * 10),
            "humor_attempted": True,
            "captain_obvious_mode": level >= 5
        }
    })


async def bring_your_own(tool_name: str, code: str, runtime: str = "python", 
                         timeout: int = 30, args: Optional[Dict[str, Any]] = None,
                         persist: bool = False, ctx: Optional[Context] = None) -> str:
    """
    Temporarily hijack the MCP server to run custom tool code.
    This allows models to define and execute their own tools on the fly.
    
    Args:
        tool_name: Name for the temporary tool
        code: The code to execute (must define an async function)
        runtime: Runtime environment (python, javascript, bash)
        timeout: Maximum execution time in seconds
        args: Arguments to pass to the custom tool
        persist: Whether to save this tool for future use
        ctx: Optional context
    
    Returns:
        The result of executing the custom tool
    
    Security Note: This is intentionally powerful and dangerous.
    Use with caution and proper sandboxing in production.
    """
    import tempfile
    import asyncio
    import hashlib
    import pickle
    
    # Security check (basic - you'd want more in production)
    if ctx and ctx.user:
        user_id = ctx.user.get("sub", "anonymous")
        # Check if user is allowed to bring their own tools
        if user_id != "system" and not user_id.startswith("admin"):
            # Rate limit non-admin users
            rate_limit_key = f"byo_tool_{user_id}"
            # Simple in-memory rate limiting (use Redis in production)
            if not hasattr(bring_your_own, "_rate_limits"):
                bring_your_own._rate_limits = {}
            
            last_call = bring_your_own._rate_limits.get(rate_limit_key, 0)
            now = datetime.now(timezone.utc).timestamp()
            if now - last_call < 10:  # 10 second cooldown
                return create_response(False, 
                    message=f"Rate limited. Please wait {10 - (now - last_call):.1f} seconds")
            bring_your_own._rate_limits[rate_limit_key] = now
    else:
        user_id = "anonymous"
    
    # Validate runtime
    allowed_runtimes = ["python", "javascript", "bash"]
    if runtime not in allowed_runtimes:
        return create_response(False, 
            message=f"Invalid runtime. Allowed: {allowed_runtimes}")
    
    # Create a unique ID for this tool
    tool_id = hashlib.md5(f"{tool_name}_{code}_{datetime.now(timezone.utc)}".encode()).hexdigest()[:8]
    full_tool_name = f"byo_{tool_name}_{tool_id}"
    
    logger.warning(f"BYO Tool execution requested: {full_tool_name} by {user_id}")
    
    try:
        if runtime == "python":
            # Create a temporary module for the code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                # Wrap the code in a module structure
                module_code = f"""
import asyncio
import json
from datetime import datetime

# User-provided code
{code}

# Execution wrapper
async def _execute_byo_tool(args):
    if 'main' in globals():
        if asyncio.iscoroutinefunction(main):
            return await main(**args)
        else:
            return main(**args)
    else:
        raise ValueError("No 'main' function defined in custom tool code")
"""
                f.write(module_code)
                temp_file = f.name
            
            # Execute the code with timeout
            try:
                # Import and run the temporary module
                import importlib.util
                spec = importlib.util.spec_from_file_location(full_tool_name, temp_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Execute with timeout
                result = await asyncio.wait_for(
                    module._execute_byo_tool(args or {}),
                    timeout=timeout
                )
                
                # Clean up
                os.unlink(temp_file)
                
            except asyncio.TimeoutError:
                os.unlink(temp_file)
                return create_response(False, 
                    message=f"Tool execution timed out after {timeout} seconds")
            except Exception as e:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                logger.error(f"BYO tool execution failed: {str(e)}")
                return create_response(False, 
                    message=f"Tool execution failed: {str(e)}")
        
        elif runtime == "javascript":
            # Use subprocess to run Node.js
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                js_code = f"""
{code}

// Execution wrapper
(async () => {{
    const args = {json.dumps(args or {})};
    if (typeof main === 'function') {{
        const result = await main(args);
        console.log(JSON.stringify(result));
    }} else {{
        throw new Error("No 'main' function defined");
    }}
}})();
"""
                f.write(js_code)
                temp_file = f.name
            
            try:
                proc = await asyncio.create_subprocess_exec(
                    'node', temp_file,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=timeout
                )
                os.unlink(temp_file)
                
                if proc.returncode != 0:
                    return create_response(False, 
                        message=f"JavaScript execution failed: {stderr.decode()}")
                
                result = json.loads(stdout.decode())
                
            except asyncio.TimeoutError:
                proc.kill()
                os.unlink(temp_file)
                return create_response(False, 
                    message=f"Tool execution timed out after {timeout} seconds")
        
        elif runtime == "bash":
            # Execute bash commands
            try:
                proc = await asyncio.create_subprocess_shell(
                    code,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=timeout
                )
                
                if proc.returncode != 0:
                    return create_response(False, 
                        message=f"Bash execution failed: {stderr.decode()}")
                
                result = stdout.decode()
                
            except asyncio.TimeoutError:
                proc.kill()
                return create_response(False, 
                    message=f"Tool execution timed out after {timeout} seconds")
        
        # Store execution history
        try:
            # Get user-scoped collections - use database access for custom collections
            collections = db_connection.get_collections(ctx.user if ctx else None)
            byo_collection = collections.database["byo_tools"]
            execution_record = {
                "tool_id": tool_id,
                "tool_name": tool_name,
                "full_name": full_tool_name,
                "code": code[:1000],  # Store first 1000 chars
                "runtime": runtime,
                "args": args,
                "result": str(result)[:500] if result else None,  # Store first 500 chars
                "user": user_id,
                "timestamp": datetime.now(timezone.utc),
                "persist": persist,
                "success": True
            }
            byo_collection.insert_one(execution_record)
            
            # If persist is True, save to a persistent tools collection
            if persist:
                persistent_tools = collections.database["persistent_byo_tools"]
                persistent_tools.update_one(
                    {"tool_name": tool_name},
                    {"$set": {
                        "tool_name": tool_name,
                        "code": code,
                        "runtime": runtime,
                        "created_by": user_id,
                        "created_at": datetime.now(timezone.utc),
                        "last_used": datetime.now(timezone.utc),
                        "execution_count": 1
                    }, "$inc": {"execution_count": 1}},
                    upsert=True
                )
                
        except Exception as e:
            logger.debug(f"Failed to store BYO tool execution: {e}")
        
        # Publish to MQTT for monitoring
        mqtt_publish("tools/byo/execution", {
            "tool_id": tool_id,
            "tool_name": full_tool_name,
            "runtime": runtime,
            "user": user_id,
            "success": True
        })
        
        return create_response(True, {
            "tool_id": tool_id,
            "tool_name": full_tool_name,
            "result": result,
            "runtime": runtime,
            "execution_time": f"{timeout}s max",
            "persisted": persist,
            "meta": {
                "warning": "Custom tool executed successfully. Use with caution.",
                "security_note": "This tool allows arbitrary code execution.",
                "user": user_id
            }
        })
        
    except Exception as e:
        logger.error(f"BYO tool creation/execution failed: {str(e)}")
        
        # Log failure
        try:
            # Get user-scoped collections - use database access for custom collections
            collections = db_connection.get_collections(ctx.user if ctx else None)
            byo_collection = collections.database["byo_tools"]
            byo_collection.insert_one({
                "tool_id": tool_id,
                "tool_name": tool_name,
                "error": str(e),
                "user": user_id,
                "timestamp": datetime.now(timezone.utc),
                "success": False
            })
        except:
            pass
        
        return create_response(False, 
            message=f"Failed to create/execute custom tool: {str(e)}")
