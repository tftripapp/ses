import React, { useState } from 'react';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Railway'de API_URL boş bırakılırsa kendi domainini kullanır
  const API_URL = '';

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
  if (!file) {
    setError('Lütfen bir dosya seçin.');
    return;
  }
  setLoading(true);
  setError(null);
  setResult(null);
  const formData = new FormData();
  formData.append('file', file);
  try {
    const res = await fetch(`/api/transcribe`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json();
      setError(err.detail || 'Bir hata oluştu.');
      setLoading(false);
      return;
    }
    const data = await res.json();
    // ... polling kodu ...
  } catch (e) {
    setError('Bir hata oluştu.');
  }
  setLoading(false);
};
  const handleUrlTranscribe = async () => {
    if (!url) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch(`${API_URL}/api/transcribe-url`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });
      const data = await res.json();
      if (data.id) {
        // polling
        let status = data.status;
        let text = '';
        while (status === 'processing') {
          await new Promise(r => setTimeout(r, 2000));
          const poll = await fetch(`${API_URL}/api/transcriptions/${data.id}`);
          const pollData = await poll.json();
          status = pollData.status;
          text = pollData.text;
        }
        setResult(text);
      } else {
        setError('Transkript başlatılamadı.');
      }
    } catch (e) {
      setError('Bir hata oluştu.');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-xl p-8 max-w-lg w-full">
        <h1 className="text-3xl font-bold mb-6 text-center text-indigo-700">Ses & Video Transkript</h1>
        <div className="mb-4">
          <label className="block mb-2 font-medium">Dosya Yükle</label>
          <input type="file" accept="audio/*,video/*" onChange={handleFileChange} className="mb-2" />
          <button onClick={handleUpload} disabled={!file || loading} className="w-full bg-indigo-600 text-white py-2 rounded-lg font-semibold hover:bg-indigo-700 transition disabled:opacity-50">Yükle & Transkript</button>
        </div>
        <div className="my-6 flex items-center justify-center">
          <span className="text-gray-400">veya</span>
        </div>
        <div className="mb-4">
          <label className="block mb-2 font-medium">Video/Ses URL</label>
          <input type="text" value={url} onChange={e => setUrl(e.target.value)} placeholder="YouTube, Vimeo..." className="w-full border rounded-lg px-3 py-2 mb-2" />
          <button onClick={handleUrlTranscribe} disabled={!url || loading} className="w-full bg-indigo-500 text-white py-2 rounded-lg font-semibold hover:bg-indigo-600 transition disabled:opacity-50">URL'den Transkript</button>
        </div>
        {loading && <div className="text-center text-indigo-600 font-medium">İşleniyor...</div>}
        {result && (
          <div className="mt-6">
            <h2 className="font-bold mb-2">Transkript Sonucu</h2>
            <textarea className="w-full border rounded-lg p-2" rows={8} value={result} readOnly />
          </div>
        )}
        {error && <div className="mt-4 text-red-500 text-center">{error}</div>}
      </div>
      <footer className="mt-8 text-gray-400 text-sm">Modern Transkript App &copy; 2024</footer>
    </div>
  );
} 
