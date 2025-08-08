import React, { useState } from 'react';
import { useQuery, useMutation } from 'convex/react';
import { api } from '../../convex/_generated/api';
import { useDropzone } from 'react-dropzone';
import { 
  FileText, 
  Upload, 
  Plane, 
  Building2, 
  Shield, 
  CreditCard, 
  FileImage,
  Calendar,
  Clock,
  MapPin,
  ExternalLink,
  Trash2,
  Eye,
  CheckCircle,
  AlertTriangle,
  Download
} from 'lucide-react';

const API_BASE = import.meta.env.DEV ? 'http://localhost:8000' : '';

const docTypes = [
  { id: 'flight', name: 'Flight', icon: Plane, color: 'bg-blue-100 text-blue-700' },
  { id: 'hotel', name: 'Hotel', icon: Building2, color: 'bg-green-100 text-green-700' },
  { id: 'visa', name: 'Visa', icon: Shield, color: 'bg-purple-100 text-purple-700' },
  { id: 'passport', name: 'Passport', icon: CreditCard, color: 'bg-red-100 text-red-700' },
  { id: 'insurance', name: 'Insurance', icon: Shield, color: 'bg-orange-100 text-orange-700' },
  { id: 'other', name: 'Other', icon: FileText, color: 'bg-gray-100 text-gray-700' },
];

function DocTypeCard({ type, count, onClick, isSelected }) {
  const Icon = type.icon;
  
  return (
    <button
      onClick={() => onClick(type.id)}
      className={`p-4 rounded-lg border-2 transition-all ${
        isSelected 
          ? 'border-blue-500 bg-blue-50' 
          : 'border-gray-200 hover:border-gray-300 bg-white'
      }`}
    >
      <div className={`w-12 h-12 rounded-full ${type.color} flex items-center justify-center mb-3 mx-auto`}>
        <Icon className="w-6 h-6" />
      </div>
      <h3 className="font-medium text-gray-800">{type.name}</h3>
      <p className="text-sm text-gray-500">{count} document{count !== 1 ? 's' : ''}</p>
    </button>
  );
}

function DocumentCard({ doc, onDelete, onView }) {
  const docType = docTypes.find(type => type.id === doc.docType);
  const Icon = docType?.icon || FileText;

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getStatusColor = (doc) => {
    if (doc.docType === 'flight' && doc.extractedData?.departureTime) {
      const depTime = new Date(doc.extractedData.departureTime);
      const now = new Date();
      const hoursUntil = (depTime - now) / (1000 * 60 * 60);
      
      if (hoursUntil < 0) return 'text-gray-500'; // Past flight
      if (hoursUntil < 24) return 'text-red-600'; // Less than 24 hours
      if (hoursUntil < 72) return 'text-orange-600'; // Less than 72 hours
      return 'text-green-600'; // Future flight
    }
    
    return 'text-green-600';
  };

  const getCheckInStatus = (doc) => {
    if (doc.docType !== 'flight' || !doc.extractedData?.departureTime) return null;
    
    const depTime = new Date(doc.extractedData.departureTime);
    const now = new Date();
    const hoursUntil = (depTime - now) / (1000 * 60 * 60);
    
    if (hoursUntil < 0) return { status: 'past', text: 'Flight completed' };
    if (hoursUntil <= 24 && hoursUntil > 2) return { status: 'available', text: 'Check-in available' };
    if (hoursUntil <= 2) return { status: 'closing', text: 'Check-in closing soon' };
    return { status: 'future', text: `Check-in opens in ${Math.floor(hoursUntil - 24)}h` };
  };

  const handleCheckIn = async () => {
    if (doc.extractedData?.checkInUrl) {
      window.open(doc.extractedData.checkInUrl, '_blank');
    } else if (doc.extractedData?.airline) {
      // Generate airline website URL
      const airlineWebsites = {
        'American Airlines': 'https://www.aa.com',
        'Delta': 'https://www.delta.com',
        'United': 'https://www.united.com',
        'Southwest': 'https://www.southwest.com',
      };
      const url = airlineWebsites[doc.extractedData.airline] || 'https://google.com/search?q=' + encodeURIComponent(doc.extractedData.airline + ' check in');
      window.open(url, '_blank');
    }
  };

  const checkInStatus = getCheckInStatus(doc);

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3 flex-1">
          <div className={`w-10 h-10 rounded-full ${docType?.color} flex items-center justify-center`}>
            <Icon className="w-5 h-5" />
          </div>
          
          <div className="flex-1">
            <h3 className="font-medium text-gray-800 mb-1">{doc.title}</h3>
            <p className="text-sm text-gray-500 mb-2">
              Uploaded {formatDate(doc.createdAt)}
            </p>
            
            {/* Flight-specific info */}
            {doc.docType === 'flight' && doc.extractedData && (
              <div className="space-y-2">
                <div className="flex items-center gap-4 text-sm">
                  {doc.extractedData.flightNumber && (
                    <span className="font-medium text-blue-600">
                      {doc.extractedData.airline} {doc.extractedData.flightNumber}
                    </span>
                  )}
                  {doc.extractedData.pnr && (
                    <span className="bg-gray-100 px-2 py-1 rounded text-gray-600">
                      PNR: {doc.extractedData.pnr}
                    </span>
                  )}
                </div>
                
                {doc.extractedData.departureTime && (
                  <div className={`text-sm ${getStatusColor(doc)}`}>
                    <Calendar className="w-4 h-4 inline mr-1" />
                    {formatDate(doc.extractedData.departureTime)}
                  </div>
                )}
                
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  {doc.extractedData.seat && (
                    <span>Seat: {doc.extractedData.seat}</span>
                  )}
                  {doc.extractedData.terminal && (
                    <span>Terminal: {doc.extractedData.terminal}</span>
                  )}
                  {doc.extractedData.gate && (
                    <span>Gate: {doc.extractedData.gate}</span>
                  )}
                </div>
                
                {checkInStatus && (
                  <div className="flex items-center justify-between bg-gray-50 rounded px-3 py-2">
                    <span className={`text-sm font-medium ${
                      checkInStatus.status === 'available' ? 'text-green-600' :
                      checkInStatus.status === 'closing' ? 'text-red-600' :
                      'text-gray-600'
                    }`}>
                      {checkInStatus.text}
                    </span>
                    {checkInStatus.status === 'available' && (
                      <button
                        onClick={handleCheckIn}
                        className="flex items-center gap-1 px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
                      >
                        <ExternalLink className="w-3 h-3" />
                        Check In
                      </button>
                    )}
                  </div>
                )}
              </div>
            )}
            
            {/* Hotel-specific info */}
            {doc.docType === 'hotel' && doc.extractedData && (
              <div className="space-y-1 text-sm text-gray-600">
                {doc.extractedData.confirmation_number && (
                  <div>Confirmation: {doc.extractedData.confirmation_number}</div>
                )}
                {doc.extractedData.check_in && (
                  <div>Check-in: {formatDate(doc.extractedData.check_in)}</div>
                )}
                {doc.extractedData.check_out && (
                  <div>Check-out: {formatDate(doc.extractedData.check_out)}</div>
                )}
              </div>
            )}
          </div>
        </div>
        
        <div className="flex items-center gap-2 ml-4">
          <button
            onClick={() => onView(doc)}
            className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded"
            title="View document"
          >
            <Eye className="w-4 h-4" />
          </button>
          <button
            onClick={() => onDelete(doc._id)}
            className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded"
            title="Delete document"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

function UploadModal({ isOpen, onClose, selectedDocType, onUpload, tripId }) {
  const [isUploading, setIsUploading] = useState(false);
  const [title, setTitle] = useState('');

  const { getRootProps, getInputProps, isDragActive, acceptedFiles } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg'],
      'text/*': ['.txt'],
    },
    maxFiles: 1,
    onDrop: (files) => {
      if (files.length > 0 && !title) {
        setTitle(files[0].name.replace(/\.[^/.]+$/, ''));
      }
    }
  });

  const handleUpload = async () => {
    if (acceptedFiles.length === 0 || !title) return;
    
    setIsUploading(true);
    
    try {
      // In a real implementation, you'd upload the file to a storage service
      // For now, we'll simulate the upload and OCR process
      
      const formData = new FormData();
      formData.append('file', acceptedFiles[0]);
      formData.append('doc_type', selectedDocType);
      formData.append('title', title);
      
      // Simulate file upload and OCR processing
      const response = await fetch(`${API_BASE}/api/documents/upload`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          doc_type: selectedDocType,
          file_name: acceptedFiles[0].name,
          title: title,
          trip_id: tripId,
        }),
      });
      
      if (!response.ok) throw new Error('Upload failed');
      
      const result = await response.json();
      
      // Save to Convex with extracted data
      // Generate a proper file URL (in production, this would be from a cloud storage service)
      const fileUrl = result.file_url || `${window.location.origin}/uploads/${result.document_id || Date.now()}`;
      
      await onUpload({
        tripId: tripId,
        docType: selectedDocType,
        title: title,
        fileUrl: fileUrl,
        extractedData: result.extracted_data,
      });
      
      onClose();
      setTitle('');
    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  if (!isOpen) return null;

  const docType = docTypes.find(type => type.id === selectedDocType);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 className="text-xl font-semibold mb-4">Upload {docType?.name} Document</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Document Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter document title"
            />
          </div>
          
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <input {...getInputProps()} />
            <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            {acceptedFiles.length > 0 ? (
              <div>
                <p className="font-medium text-green-600 mb-2">File selected:</p>
                <p className="text-sm text-gray-600">{acceptedFiles[0].name}</p>
              </div>
            ) : (
              <div>
                <p className="text-gray-600 mb-2">
                  {isDragActive ? 'Drop your file here' : 'Drag & drop your document here'}
                </p>
                <p className="text-sm text-gray-500">
                  Supports PDF, JPG, PNG files
                </p>
              </div>
            )}
          </div>
          
          <div className="text-xs text-gray-500 bg-blue-50 p-3 rounded">
            <CheckCircle className="w-4 h-4 inline mr-1" />
            We'll automatically extract important information like flight details, booking numbers, and dates using OCR technology.
          </div>
        </div>
        
        <div className="flex gap-3 mt-6">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            disabled={isUploading}
          >
            Cancel
          </button>
          <button
            onClick={handleUpload}
            disabled={acceptedFiles.length === 0 || !title || isUploading}
            className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isUploading ? 'Processing...' : 'Upload & Process'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function TravelDocsManager({ tripId }) {
  const allDocs = useQuery(api.travelDocs.getUserDocs, { tripId }) || [];
  const uploadDocument = useMutation(api.travelDocs.uploadDocument);
  const deleteDocument = useMutation(api.travelDocs.deleteDocument);
  const flightCheckIns = useQuery(api.travelDocs.getFlightCheckIns) || [];
  
  const [selectedDocType, setSelectedDocType] = useState('all');
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadDocType, setUploadDocType] = useState('flight');
  const [viewingDoc, setViewingDoc] = useState(null);

  const filteredDocs = selectedDocType === 'all' 
    ? allDocs 
    : allDocs.filter(doc => doc.docType === selectedDocType);

  const docCounts = docTypes.reduce((acc, type) => {
    acc[type.id] = allDocs.filter(doc => doc.docType === type.id).length;
    return acc;
  }, {});

  const handleUploadDocument = async (docData) => {
    try {
      await uploadDocument(docData);
    } catch (error) {
      console.error('Error uploading document:', error);
      alert('Failed to upload document');
    }
  };

  const handleDeleteDocument = async (docId) => {
    if (confirm('Are you sure you want to delete this document?')) {
      try {
        await deleteDocument({ docId });
      } catch (error) {
        console.error('Error deleting document:', error);
      }
    }
  };

  const openUploadModal = (docType) => {
    setUploadDocType(docType);
    setShowUploadModal(true);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">Travel Documents</h1>
        <p className="text-gray-600">
          Upload and manage all your travel documents in one place. We'll automatically extract key information.
        </p>
      </div>

      {/* Check-in Alerts */}
      {flightCheckIns.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-blue-800 mb-2">
            <Plane className="w-5 h-5" />
            <h3 className="font-semibold">Flight Check-in Available</h3>
          </div>
          <div className="space-y-2">
            {flightCheckIns.map(doc => (
              <div key={doc._id} className="flex items-center justify-between bg-white rounded p-3">
                <div>
                  <div className="font-medium">{doc.title}</div>
                  <div className="text-sm text-gray-600">
                    {doc.extractedData?.airline} {doc.extractedData?.flightNumber}
                  </div>
                </div>
                <button
                  onClick={() => window.open(doc.extractedData?.checkInUrl || '#', '_blank')}
                  className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                  Check In
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Document Type Filter */}
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-800">Document Categories</h2>
          <button
            onClick={() => openUploadModal('flight')}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            <Upload className="w-4 h-4" />
            Upload Document
          </button>
        </div>
        
        <div className="grid grid-cols-3 md:grid-cols-6 gap-4 mb-4">
          <button
            onClick={() => setSelectedDocType('all')}
            className={`p-4 rounded-lg border-2 transition-all ${
              selectedDocType === 'all'
                ? 'border-blue-500 bg-blue-50' 
                : 'border-gray-200 hover:border-gray-300 bg-white'
            }`}
          >
            <FileText className="w-6 h-6 mx-auto mb-2 text-gray-600" />
            <h3 className="font-medium text-gray-800">All</h3>
            <p className="text-sm text-gray-500">{allDocs.length} total</p>
          </button>
          
          {docTypes.map(type => (
            <DocTypeCard
              key={type.id}
              type={type}
              count={docCounts[type.id]}
              onClick={setSelectedDocType}
              isSelected={selectedDocType === type.id}
            />
          ))}
        </div>
      </div>

      {/* Documents List */}
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">
          {selectedDocType === 'all' ? 'All Documents' : `${docTypes.find(t => t.id === selectedDocType)?.name} Documents`}
          <span className="text-gray-500 font-normal ml-2">({filteredDocs.length})</span>
        </h2>
        
        {filteredDocs.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <h3 className="text-lg font-medium text-gray-500 mb-2">No documents yet</h3>
            <p className="text-gray-400 mb-4">Upload your travel documents to get started</p>
            <div className="flex gap-2 justify-center">
              {docTypes.slice(0, 3).map(type => (
                <button
                  key={type.id}
                  onClick={() => openUploadModal(type.id)}
                  className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm"
                >
                  Add {type.name}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredDocs.map(doc => (
              <DocumentCard
                key={doc._id}
                doc={doc}
                onDelete={handleDeleteDocument}
                onView={setViewingDoc}
              />
            ))}
          </div>
        )}
      </div>

      <UploadModal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        selectedDocType={uploadDocType}
        onUpload={handleUploadDocument}
        tripId={tripId}
      />

      {/* Document Viewer Modal */}
      {viewingDoc && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-screen overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold">{viewingDoc.title}</h3>
              <button
                onClick={() => setViewingDoc(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            <div className="bg-gray-100 rounded-lg p-4 text-center">
              <FileImage className="w-16 h-16 mx-auto mb-4 text-gray-400" />
              <p className="text-gray-600">Document preview would appear here</p>
              <button className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">
                <Download className="w-4 h-4 inline mr-2" />
                Download Original
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}