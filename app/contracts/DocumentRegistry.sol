// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title DocumentRegistry
 * @dev Store document hashes for verification
 */
contract DocumentRegistry {
    // Document data structure
    struct Document {
        string documentType;
        string documentId;
        string hash;
        string metadata;
        address registeredBy;
        uint256 timestamp;
        bool isRegistered;
    }
    
    // Mapping from document type + id to document hash
    mapping(bytes32 => Document) private documents;
    
    // Events
    event DocumentRegistered(
        string documentType,
        string documentId,
        string hash,
        address registeredBy,
        uint256 timestamp
    );
    
    /**
     * @dev Register a document hash
     * @param documentType Type of document (e.g., "drawing", "contract", "rfi")
     * @param documentId Identifier for the document
     * @param hash SHA-256 hash of the document
     * @param metadata Additional metadata about the document (e.g., JSON string)
     */
    function registerDocument(
        string memory documentType,
        string memory documentId,
        string memory hash,
        string memory metadata
    ) public {
        // Create a unique key for the document
        bytes32 key = keccak256(abi.encodePacked(documentType, documentId));
        
        // Store document data
        documents[key] = Document({
            documentType: documentType,
            documentId: documentId,
            hash: hash,
            metadata: metadata,
            registeredBy: msg.sender,
            timestamp: block.timestamp,
            isRegistered: true
        });
        
        // Emit event
        emit DocumentRegistered(
            documentType,
            documentId,
            hash,
            msg.sender,
            block.timestamp
        );
    }
    
    /**
     * @dev Verify if a document hash matches what's stored
     * @param documentType Type of document
     * @param documentId Identifier for the document
     * @param hash Hash to verify
     * @return isValid True if the hash matches
     * @return registeredBy Address that registered the document
     * @return timestamp When the document was registered
     */
    function verifyDocument(
        string memory documentType,
        string memory documentId,
        string memory hash
    ) public view returns (bool isValid, address registeredBy, uint256 timestamp) {
        bytes32 key = keccak256(abi.encodePacked(documentType, documentId));
        Document memory doc = documents[key];
        
        if (!doc.isRegistered) {
            return (false, address(0), 0);
        }
        
        bool hashMatches = keccak256(abi.encodePacked(doc.hash)) == keccak256(abi.encodePacked(hash));
        
        return (hashMatches, doc.registeredBy, doc.timestamp);
    }
    
    /**
     * @dev Get document metadata
     * @param documentType Type of document
     * @param documentId Identifier for the document
     * @return isRegistered True if the document is registered
     * @return hash The stored hash
     * @return metadata Additional metadata
     * @return registeredBy Address that registered the document
     * @return timestamp When the document was registered
     */
    function getDocumentInfo(
        string memory documentType,
        string memory documentId
    ) public view returns (
        bool isRegistered,
        string memory hash,
        string memory metadata,
        address registeredBy,
        uint256 timestamp
    ) {
        bytes32 key = keccak256(abi.encodePacked(documentType, documentId));
        Document memory doc = documents[key];
        
        return (
            doc.isRegistered,
            doc.hash,
            doc.metadata,
            doc.registeredBy,
            doc.timestamp
        );
    }
}