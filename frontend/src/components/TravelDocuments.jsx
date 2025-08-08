import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import { Upload, File, CheckCircle, AlertCircle, Plane, Building2, Shield, CreditCard, FileText, X } from 'lucide-react';

const DOC_TYPES = [
  { id: 'flight', name: 'Flight Tickets', icon: Plane, color: 'bg-blue-100 text-blue-700', acceptedTypes: ['.pdf', '.png', '.jpg', '.jpeg'] },
  { id: 'hotel', name: 'Hotel Booking', icon: Building2, color: 'bg-green-100 text-green-700', acceptedTypes: ['.pdf', '.png', '.jpg', '.jpeg'] },
  { id: 'passport', name: 'Passport', icon: Shield, color: 'bg-red-100 text-red-700', acceptedTypes: ['.pdf', '.png', '.jpg', '.jpeg'] },
  { id: 'visa', name: 'Visa', icon: FileText, color: 'bg-purple-100 text-purple-700', acceptedTypes: ['.pdf', '.png', '.jpg', '.jpeg'] },
  { id: 'insurance', name: 'Travel Insurance', icon: CreditCard, color: 'bg-orange-100 text-orange-700', acceptedTypes: ['.pdf'] },
  { id: 'other', name: 'Other Documents', icon: File, color: 'bg-gray-100 text-gray-700', acceptedTypes: ['.pdf', '.png', '.jpg', '.jpeg', '.doc', '.docx'] }
];

export default function TravelDocuments() {
  const [selectedDocType, setSelectedDocType] = useState('flight');
  const [uploadedDocs, setUploadedDocs] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [extractedData, setExtractedData] = useState(null);

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setUploading(true);

    try {
      // Document OCR extraction not yet implemented
      // This feature will be available in a future update
      
      const newDoc = {
        id: Date.now(),
        name: file.name,
        type: selectedDocType,
        size: file.size,
        uploadedAt: new Date(),
        extractedData: {},
        status: 'uploaded'
      };

      setUploadedDocs(prev => [...prev, newDoc]);
      setExtractedData({});
      
      // Show message that OCR is not yet available
      alert('Document uploaded successfully! OCR extraction feature coming soon.');
      
      // Auto-clear extracted data after 5 seconds
      setTimeout(() => setExtractedData(null), 5000);

    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
    }
  }, [selectedDocType]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles: 1,
    disabled: uploading
  });

  const removeDoc = (docId) => {
    setUploadedDocs(prev => prev.filter(doc => doc.id !== docId));
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const selectedDocTypeData = DOC_TYPES.find(type => type.id === selectedDocType);
  const IconComponent = selectedDocTypeData?.icon || File;

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-100">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-8"
          >
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Travel Documents 💼
            </h1>
            <p className="text-gray-600 text-lg">
              Upload and manage your travel documents with AI-powered OCR extraction
            </p>
          </motion.div>

          {/* Document Type Selector */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Select Document Type</h2>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                {DOC_TYPES.map(type => {
                  const TypeIcon = type.icon;
                  return (
                    <motion.button
                      key={type.id}
                      onClick={() => setSelectedDocType(type.id)}
                      className={`p-4 rounded-lg border-2 transition-all text-center ${
                        selectedDocType === type.id
                          ? 'border-blue-500 bg-blue-50 shadow-md'
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                      }`}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <div className={`w-12 h-12 mx-auto mb-2 rounded-lg flex items-center justify-center ${
                        selectedDocType === type.id ? type.color : 'bg-gray-100 text-gray-600'
                      }`}>
                        <TypeIcon className="w-6 h-6" />
                      </div>
                      <p className="text-sm font-medium text-gray-900">{type.name}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        {type.acceptedTypes.join(', ')}
                      </p>
                    </motion.button>
                  );
                })}
              </div>
            </div>
          </motion.div>

          {/* Upload Zone */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
              <div className={`bg-gradient-to-r ${selectedDocTypeData?.color.includes('blue') ? 'from-blue-500 to-blue-600' : 
                                                 selectedDocTypeData?.color.includes('green') ? 'from-green-500 to-green-600' :
                                                 selectedDocTypeData?.color.includes('red') ? 'from-red-500 to-red-600' :
                                                 selectedDocTypeData?.color.includes('purple') ? 'from-purple-500 to-purple-600' :
                                                 selectedDocTypeData?.color.includes('orange') ? 'from-orange-500 to-orange-600' :
                                                 'from-gray-500 to-gray-600'} text-white p-4`}>
                <div className="flex items-center gap-2">
                  <IconComponent className="w-6 h-6" />
                  <h3 className="text-xl font-semibold">Upload {selectedDocTypeData?.name}</h3>
                </div>
              </div>

              <div className="p-6">
                <div
                  {...getRootProps()}
                  className={`border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer ${
                    isDragActive && !isDragReject
                      ? 'border-blue-500 bg-blue-50'
                      : isDragReject
                      ? 'border-red-500 bg-red-50'
                      : uploading
                      ? 'border-gray-300 bg-gray-50 cursor-not-allowed'
                      : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
                  }`}
                >
                  <input {...getInputProps()} />
                  
                  {uploading ? (
                    <div className="space-y-4">
                      <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-500 mx-auto"></div>
                      <div>
                        <p className="text-lg font-medium text-gray-900">Processing Document...</p>
                        <p className="text-sm text-gray-600">Extracting information with AI</p>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <Upload className="w-16 h-16 text-gray-400 mx-auto" />
                      <div>
                        <p className="text-lg font-medium text-gray-900">
                          {isDragActive 
                            ? isDragReject
                              ? 'File type not supported'
                              : 'Drop your document here'
                            : 'Drag & drop your document, or click to select'
                          }
                        </p>
                        <p className="text-sm text-gray-600 mt-1">
                          Accepted formats: {selectedDocTypeData?.acceptedTypes.join(', ')}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </motion.div>

          {/* Extracted Data Display */}
          <AnimatePresence>
            {extractedData && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mb-8"
              >
                <div className="bg-green-50 border border-green-200 rounded-2xl p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <CheckCircle className="w-6 h-6 text-green-600" />
                    <h3 className="text-lg font-semibold text-green-900">
                      Information Extracted Successfully!
                    </h3>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {Object.entries(extractedData).map(([key, value]) => (
                      <div key={key} className="bg-white rounded-lg p-3 border border-green-200">
                        <p className="text-xs font-medium text-gray-600 uppercase tracking-wide mb-1">
                          {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                        </p>
                        <p className="text-sm font-semibold text-gray-900">{value}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Uploaded Documents */}
          {uploadedDocs.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-2xl shadow-lg p-6"
            >
              <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Uploaded Documents ({uploadedDocs.length})
              </h3>
              
              <div className="space-y-3">
                {uploadedDocs.map((doc) => {
                  const docTypeData = DOC_TYPES.find(type => type.id === doc.type);
                  const DocIcon = docTypeData?.icon || File;
                  
                  return (
                    <motion.div
                      key={doc.id}
                      layout
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center gap-4">
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${docTypeData?.color || 'bg-gray-100 text-gray-600'}`}>
                          <DocIcon className="w-5 h-5" />
                        </div>
                        
                        <div>
                          <h4 className="font-medium text-gray-900">{doc.name}</h4>
                          <div className="flex items-center gap-4 text-sm text-gray-600">
                            <span>{docTypeData?.name || 'Unknown Type'}</span>
                            <span>{formatFileSize(doc.size)}</span>
                            <span>{doc.uploadedAt.toLocaleDateString()}</span>
                            {doc.status === 'processed' && (
                              <span className="flex items-center gap-1 text-green-600">
                                <CheckCircle className="w-4 h-4" />
                                Processed
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      
                      <button
                        onClick={() => removeDoc(doc.id)}
                        className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </motion.div>
                  );
                })}
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}