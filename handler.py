import json
import logging
from mangum import Mangum

# Configure logging for Lambda
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Test bcrypt import early to catch issues
    import bcrypt
    logger.info(f"bcrypt imported successfully, version: {getattr(bcrypt, '__version__', 'Unknown')}")
    
    from passlib.context import CryptContext
    # Test passlib + bcrypt combination
    test_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    logger.info("passlib + bcrypt combination working")
    
except Exception as e:
    logger.error(f"bcrypt/passlib import error: {e}")
    # This will help diagnose the exact issue in CloudWatch logs

try:
    from main import app
    logger.info("FastAPI app imported successfully")
except Exception as e:
    logger.error(f"FastAPI app import error: {e}")
    raise

# AWS Lambda handler with better error handling
def handler(event, context):
    """
    AWS Lambda handler with enhanced error logging
    """
    try:
        logger.info(f"Lambda event: {json.dumps(event, default=str)[:500]}...")  # Truncate for logging
        
        # Create Mangum handler
        mangum_handler = Mangum(app, lifespan="off")
        
        # Process the request
        response = mangum_handler(event, context)
        
        logger.info(f"Response status: {response.get('statusCode', 'Unknown')}")
        return response
        
    except Exception as e:
        logger.error(f"Handler error: {str(e)}", exc_info=True)
        
        # Return a proper HTTP error response
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
            },
            "body": json.dumps({
                "detail": "Internal server error",
                "error": str(e)[:200]  # Truncate error message
            })
        }