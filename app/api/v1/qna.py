from fastapi import APIRouter, UploadFile, File, Depends, Body, HTTPException
import os
import hashlib
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schema.qna import QnARequest, QnAResponse
from app.services.qna_service import handle_document_query
from app.crud.uploaded_file import get_uploaded_files, insert_uploaded_files, get_uploaded_file
from app.auth.dependencies import get_current_user
from app.faiss.faiss_vector_store import check_vectorstore_exists, get_or_create_vectorstore
from app.core.dependencies import get_embedding_model
from uuid import UUID

router = APIRouter()

# Add embeddings initialization at the top with other imports
embeddings = get_embedding_model()

@router.post("/upload", status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Upload and store a document for the authenticated user."""
    try:
        # Verify file extension first
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ['.pdf', '.txt', '.png', '.jpg', '.jpeg']:
            return {
                "error": "Unsupported file format. Please use PDF, TXT, or image files (PNG, JPG, JPEG)."
            }

        content = await file.read()
        file_hash = hashlib.md5(content).hexdigest()
        
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, file.filename)
        
        # Write new file
        with open(file_path, "wb") as f:
            f.write(content)

        # Save to database to get UUID
        uploaded_file = insert_uploaded_files(db, current_user.id, file.filename, file_path)

        # Process and embed the document using UUID
        vectorstore = get_or_create_vectorstore(
            file_id=uploaded_file.id,  # This is now a UUID string
            file_path=file_path,
            embeddings=embeddings
        )
        
        if isinstance(vectorstore, str):  # Error message
            return {"error": f"Failed to process document: {vectorstore}"}

        return {
            "message": "File uploaded and processed successfully",
            "file_id": uploaded_file.id,  # Return the UUID
            "file_name": file.filename
        }
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        return {"error": str(e)}

@router.get("/documents")
def get_uploaded_documents(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Retrieve list of uploaded documents for the authenticated user."""
    uploaded_files = get_uploaded_files(db, current_user.id)

    return {
        "documents": [
            {
                "file_id": file.id,  # This is the UUID
                "file_name": file.file_name,
                "upload_time": file.upload_time
            }
            for file in uploaded_files
        ]
    }

@router.post("/ask", response_model=QnAResponse)
async def ask_question(
    request: QnARequest = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Ask questions about a previously uploaded document for the logged-in user."""
    uploaded_file = get_uploaded_file(db, current_user.id, str(request.file_id))  # Convert UUID to string

    if not uploaded_file:
        return QnAResponse(
            query=request.query,
            answer="Error: File not found. Please upload the file first.",
            references=""
        )

    # Verify file exists and is accessible
    if not os.path.exists(uploaded_file.file_path):
        return QnAResponse(
            query=request.query,
            answer="Error: File not found in storage. Please upload the file again.",
            references=""
        )

    # Verify file extension
    file_extension = os.path.splitext(uploaded_file.file_path)[1].lower()
    if file_extension not in ['.pdf', '.txt', '.png', '.jpg', '.jpeg']:
        return QnAResponse(
            query=request.query,
            answer="Error: Only PDF, TXT, and image files (PNG, JPG, JPEG) are supported.",
            references=""
        )

    return await handle_document_query(request, uploaded_file)
