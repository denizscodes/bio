"use client";

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Droplets, Leaf, Zap, BarChart3, Search, Activity, Trash2, LineChart, Globe, Info, CheckCircle2, Box, History, TrendingUp, PlusCircle, Edit3, Save, XCircle, RefreshCw, AlertTriangle } from 'lucide-react';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [retraining, setRetraining] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [tab, setTab] = useState<'scan' | 'inventory' | 'trends'>('scan');
  const [metricTab, setMetricTab] = useState<'cm' | 'roc' | 'metrics'>('cm');
  const [distance, setDistance] = useState(5);
  const [volume, setVolume] = useState(1.0);
  const [historyData, setHistoryData] = useState<any>(null);
  const [editingDate, setEditingDate] = useState<string | null>(null);
  const [editWeight, setEditWeight] = useState<string>("");

  const fetchHistory = async () => {
    try {
      const res = await fetch('http://localhost:8000/history');
      const data = await res.json();
      setHistoryData(data);
    } catch (e) {
      console.error("History fetch failed", e);
    }
  };

  useEffect(() => { fetchHistory(); }, []);

  const handlePredict = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('distance', distance.toString());
    formData.append('volume', volume.toString());

    try {
      const res = await fetch('http://localhost:8000/predict', { method: 'POST', body: formData });
      if (!res.ok) throw new Error("Analiz başarısız");
      const data = await res.json();
      setResult(data);
    } catch (error: any) { alert(error.message); } finally { setLoading(false); }
  };

  const addToInventory = async () => {
    if (!result) return;
    try {
      await fetch('http://localhost:8000/add-to-inventory', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: result.waste_type, weight: result.calculated_weight_g, impact: result.impact })
      });
      alert("Envantere eklendi!");
      fetchHistory();
    } catch (e) { alert("Ekleme hatası"); }
  };

  const deliverInventory = async () => {
    try {
      const res = await fetch('http://localhost:8000/deliver-inventory', { method: 'POST' });
      if (!res.ok) throw new Error("Teslimat başarısız");
      const data = await res.json();
      alert(`TEBRİKLER!\n\n${data.delivered_weight_kg} kg atık geri dönüşüme kazandırıldı.`);
      fetchHistory();
    } catch (e) { alert("Envanter boş veya bir hata oluştu"); }
  };

  const deleteRecord = async (date: string) => {
    if (!confirm(`${date} tarihli kaydı silmek istediğinize emin misiniz? Bu RNN modelini etkiler.`)) return;
    try {
      await fetch('http://localhost:8000/history/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ date })
      });
      fetchHistory();
    } catch (e) { alert("Silme hatası"); }
  };

  const updateWeight = async (date: string) => {
    try {
      await fetch('http://localhost:8000/history/edit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ date, weight_kg: parseFloat(editWeight) })
      });
      setEditingDate(null);
      fetchHistory();
    } catch (e) { alert("Güncelleme hatası"); }
  };

  const retrainRNN = async () => {
    setRetraining(true);
    try {
      await fetch('http://localhost:8000/rnn/retrain', { method: 'POST' });
      alert("Yapay Zeka başarıyla güncellendi ve yeni grafik oluşturuldu!");
      fetchHistory();
    } catch (e) { alert("Eğitim hatası"); } finally { setRetraining(false); }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="bg-white border-b border-slate-200 sticky top-0 z-20">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-emerald-600 p-2 rounded-xl shadow-lg shadow-emerald-200"><Globe className="text-white w-6 h-6 animate-spin-slow" /></div>
            <div className="flex flex-col">
              <span className="text-xl font-black text-slate-900 leading-none">EcoGuard</span>
              <span className="text-[10px] font-bold text-emerald-600 uppercase tracking-widest mt-1">Smart Recycle AI</span>
            </div>
          </div>
          <div className="flex bg-slate-100 p-1.5 rounded-2xl gap-1">
            <button onClick={() => setTab('scan')} className={`px-6 py-2.5 rounded-xl text-xs font-bold transition-all ${tab === 'scan' ? 'bg-white text-emerald-700 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}>Analiz</button>
            <button onClick={() => setTab('inventory')} className={`px-6 py-2.5 rounded-xl text-xs font-bold transition-all ${tab === 'inventory' ? 'bg-white text-emerald-700 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}>Envanter</button>
            <button onClick={() => setTab('trends')} className={`px-6 py-2.5 rounded-xl text-xs font-bold transition-all ${tab === 'trends' ? 'bg-white text-emerald-700 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}>Trend Analizi</button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-10">
        <AnimatePresence mode="wait">
          {tab === 'scan' && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="grid grid-cols-1 lg:grid-cols-12 gap-10">
              <div className="lg:col-span-5 space-y-8">
                <div className="bg-white rounded-[2.5rem] p-10 shadow-xl shadow-slate-200 border border-slate-100">
                  <h3 className="text-xl font-black text-slate-800 mb-8 flex items-center gap-3"><Activity className="text-emerald-500" /> Atık Tanımlama</h3>
                  <div className="space-y-8">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-3">
                         <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Tahmini Hacim</label>
                         <div className="bg-slate-50 px-4 py-3 rounded-2xl border border-slate-100 flex items-center justify-between">
                            <span className="text-sm font-black text-emerald-600">{volume} L</span>
                            <input type="range" min="0.1" max="200" step="0.5" value={volume} onChange={(e) => setVolume(parseFloat(e.target.value))} className="w-24 accent-emerald-600" />
                         </div>
                      </div>
                      <div className="space-y-3">
                         <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Tesis Uzaklığı</label>
                         <div className="bg-slate-50 px-4 py-3 rounded-2xl border border-slate-100 flex items-center justify-between">
                            <span className="text-sm font-black text-blue-600">{distance} km</span>
                            <input type="range" min="1" max="100" value={distance} onChange={(e) => setDistance(parseInt(e.target.value))} className="w-24 accent-blue-600" />
                         </div>
                      </div>
                    </div>
                    <label className="relative block group cursor-pointer">
                      <div className={`border-2 border-dashed rounded-[2rem] p-10 transition-all flex flex-col items-center justify-center gap-5 ${file ? 'border-emerald-500 bg-emerald-50/20' : 'border-slate-200 bg-slate-50/50 hover:bg-slate-50'}`}>
                        {preview ? <img src={preview} alt="Arşiv" className="w-full h-64 object-cover rounded-3xl shadow-lg border-8 border-white" /> : (
                          <>
                            <div className="bg-white p-6 rounded-3xl shadow-sm text-emerald-500 group-hover:scale-110 transition-transform"><Upload className="w-10 h-10" /></div>
                            <div className="text-center"><p className="text-sm font-black text-slate-700">Fotoğraf Yükle veya Sürükle</p></div>
                          </>
                        )}
                        <input type="file" className="hidden" onChange={(e) => { if (e.target.files?.[0]) { setFile(e.target.files[0]); setPreview(URL.createObjectURL(e.target.files[0])); } }} />
                      </div>
                    </label>
                    <button onClick={handlePredict} disabled={!file || loading} className="w-full py-5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-2xl font-black text-sm shadow-xl shadow-emerald-200 transition-all disabled:opacity-50">
                      {loading ? "Analiz Ediliyor..." : "Analiz Et"}
                    </button>
                  </div>
                </div>
              </div>

              <div className="lg:col-span-7 space-y-8">
                {result ? (
                  <div className="space-y-8">
                    <div className="bg-white rounded-[2.5rem] p-10 shadow-xl shadow-slate-200 relative overflow-hidden">
                       <div className="absolute top-0 right-0 p-10">
                          <div className={`px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest ${result.is_recyclable ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'}`}>{result.is_recyclable ? "Geri Dönüştürülebilir" : "Geri Dönüşmez"}</div>
                       </div>
                       <div className="space-y-2 mb-10">
                          <p className="text-[10px] font-black text-emerald-500 uppercase tracking-widest">Model Tahmini</p>
                          <div className="flex items-baseline gap-4">
                            <h2 className="text-6xl font-black text-slate-900 tracking-tighter">{result.waste_type}</h2>
                          </div>
                       </div>
                       <div className="border-t border-slate-100 pt-8 mt-8">
                          <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4">KNN Benzerlik Analizi</p>
                          <div className="flex gap-3">
                            {result.similar_items.map((item: any, i: number) => (
                              <div key={i} className="px-5 py-3 bg-slate-50 rounded-2xl border border-slate-100 text-xs font-black text-slate-600 flex items-center gap-2"><Search className="w-3 h-3 text-slate-400" /> {item.toUpperCase()}</div>
                            ))}
                          </div>
                       </div>
                       <div className="grid grid-cols-3 gap-6 mt-10">
                          <div className="bg-emerald-50 p-6 rounded-3xl border border-emerald-100"><Leaf className="text-emerald-500 mb-3" /><p className="text-2xl font-black text-emerald-900">{result.impact.trees_saved}</p><p className="text-[10px] font-bold text-emerald-600 uppercase">Ağaç</p></div>
                          <div className="bg-blue-50 p-6 rounded-3xl border border-blue-100"><Droplets className="text-blue-500 mb-3" /><p className="text-2xl font-black text-blue-900">{result.impact.water_saved}</p><p className="text-[10px] font-bold text-blue-600 uppercase">Su (Lt)</p></div>
                          <div className="bg-slate-50 p-6 rounded-3xl border border-slate-100"><Activity className="text-emerald-500 mb-3" /><p className="text-2xl font-black text-slate-900">{result.impact.net_co2}</p><p className="text-[10px] font-bold text-slate-500 uppercase">Net CO2 (Kg)</p></div>
                       </div>
                       <button onClick={addToInventory} className="mt-10 w-full flex items-center justify-center gap-3 py-4 border-2 border-emerald-200 text-emerald-700 bg-emerald-50/50 rounded-2xl font-black text-xs hover:bg-emerald-100 transition-all"><PlusCircle className="w-4 h-4" /> ENVANTERE EKLE</button>
                    </div>

                    <div className="bg-white rounded-[2.5rem] p-10 shadow-sm border border-slate-100">
                      <div className="flex justify-between items-center mb-8">
                        <h4 className="font-black text-slate-800 flex items-center gap-3"><BarChart3 className="text-blue-500" /> Model Doğrulama</h4>
                        <div className="flex bg-slate-100 p-1 rounded-xl">
                          <button onClick={() => setMetricTab('cm')} className={`px-4 py-1.5 rounded-lg text-[10px] font-bold ${metricTab === 'cm' ? 'bg-white shadow-sm' : 'text-slate-400'}`}>CM</button>
                          <button onClick={() => setMetricTab('roc')} className={`px-4 py-1.5 rounded-lg text-[10px] font-bold ${metricTab === 'roc' ? 'bg-white shadow-sm' : 'text-slate-400'}`}>ROC</button>
                          <button onClick={() => setMetricTab('metrics')} className={`px-4 py-1.5 rounded-lg text-[10px] font-bold ${metricTab === 'metrics' ? 'bg-white shadow-sm' : 'text-slate-400'}`}>F1</button>
                        </div>
                      </div>
                      <img src={metricTab === 'cm' ? result.cm_url : metricTab === 'roc' ? result.roc_url : result.metrics_url} className="w-full rounded-2xl" />
                    </div>
                  </div>
                ) : (
                  <div className="h-full min-h-[600px] border-4 border-dashed border-slate-200 rounded-[3rem] flex flex-col items-center justify-center p-20 text-center opacity-50"><Box className="w-20 h-20 text-slate-300 mb-8" /><h4 className="text-2xl font-black text-slate-400">Veri Bekleniyor</h4></div>
                )}
              </div>
            </motion.div>
          )}

          {tab === 'inventory' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
              <div className="flex flex-col md:flex-row justify-between items-center gap-6 bg-white p-10 rounded-[2.5rem] shadow-sm border border-slate-100">
                  <div><h3 className="text-2xl font-black text-slate-900 tracking-tight">Toplanan Atıklar</h3><p className="text-sm font-medium text-slate-400 mt-2">{historyData?.inventory?.length || 0} öğe teslimat bekliyor.</p></div>
                  <button onClick={deliverInventory} className="px-10 py-5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-[2rem] font-black text-sm shadow-xl shadow-emerald-200 transition-all flex items-center gap-3"><CheckCircle2 className="w-5 h-5" /> ŞİMDİ TESLİM ET</button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                 {historyData?.inventory?.map((item: any, i: number) => (
                   <div key={i} className="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100 relative group overflow-hidden">
                      <p className="text-[10px] font-black text-emerald-500 uppercase tracking-widest mb-2">{item.date}</p>
                      <h4 className="text-3xl font-black text-slate-900 mb-6">{item.type}</h4>
                      <div className="flex justify-between text-xs font-bold text-slate-500 uppercase"><span>Ağırlık</span><span className="text-slate-900">{item.weight} gr</span></div>
                   </div>
                 ))}
              </div>
            </motion.div>
          )}

          {tab === 'trends' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-10">
              <div className="bg-emerald-900 rounded-[3rem] p-12 text-white relative overflow-hidden">
                 <div className="relative z-10 grid grid-cols-1 md:grid-cols-2 gap-10">
                    <div>
                      <h3 className="text-3xl font-black mb-8 flex items-center gap-4"><TrendingUp /> RNN Tahmin Motoru</h3>
                      <div className="bg-white/10 p-10 rounded-[2.5rem] border border-white/10">
                         <p className="text-xs font-bold uppercase tracking-widest text-emerald-300 mb-4">Gelecek Ay Projeksiyonu</p>
                         <div className="flex items-baseline gap-4"><span className="text-7xl font-black tracking-tighter">+{historyData?.next_month_forecast_kg}</span><span className="text-xl font-bold opacity-60 uppercase">Kg</span></div>
                      </div>
                      <button 
                        onClick={retrainRNN} 
                        disabled={retraining}
                        className={`mt-10 w-full flex items-center justify-center gap-3 py-4 rounded-2xl font-black text-xs transition-all ${retraining ? 'bg-slate-700 opacity-50' : 'bg-emerald-500 hover:bg-emerald-400 text-white'}`}
                      >
                        {retraining ? <RefreshCw className="animate-spin w-4 h-4" /> : <RefreshCw className="w-4 h-4" />} MODELİ YENİDEN EĞİT
                      </button>
                    </div>

                    <div className="bg-emerald-800/50 p-10 rounded-[2.5rem]">
                       <p className="text-[10px] font-black uppercase text-emerald-400 mb-8">Model Performans Grafiği (Tüm Yıl)</p>
                       <img src={`http://localhost:8000/static/forecast_performance.png?t=${Date.now()}`} className="w-full rounded-xl border border-white/10" alt="Forecast Performance" />
                    </div>
                 </div>
              </div>

              {/* Editable History Table */}
              <div className="bg-white rounded-[3rem] p-12 border border-slate-100 shadow-sm relative">
                 <div className="flex items-center justify-between mb-8">
                    <h5 className="text-xl font-black text-slate-800 flex items-center gap-3"><History className="text-emerald-500" /> Veri Kayıtları</h5>
                    <div className="flex items-center gap-2 bg-amber-50 px-4 py-2 rounded-xl text-amber-700 text-[10px] font-black"><AlertTriangle className="w-3 h-3" /> VERİLER RNN MODELİNİ DOĞRUDAN ETKİLER</div>
                 </div>
                 <div className="max-h-96 overflow-y-auto pr-4 custom-scrollbar">
                    <table className="w-full">
                       <thead className="sticky top-0 bg-white shadow-sm"><tr className="text-left border-b border-slate-50 text-[10px] font-black text-slate-400 uppercase tracking-widest"><th className="pb-4">Tarih</th><th className="pb-4 text-right">Kg</th><th className="pb-4 text-right px-6">İşlemler</th></tr></thead>
                       <tbody className="divide-y divide-slate-50">
                          {historyData?.daily_history?.slice().reverse().map((row: any, i: number) => (
                             <tr key={i} className="group hover:bg-slate-50/50">
                                <td className="py-4 text-xs font-bold text-slate-600">{row.date}</td>
                                <td className="py-4 text-right">
                                  {editingDate === row.date ? (
                                    <input type="number" step="0.1" value={editWeight} onChange={(e) => setEditWeight(e.target.value)} className="w-20 bg-slate-100 border-none rounded-lg px-2 py-1 text-xs font-black" />
                                  ) : (
                                    <span className="text-xs font-black text-slate-900">{row.weight_kg.toFixed(2)} kg</span>
                                  )}
                                </td>
                                <td className="py-4 text-right px-6 space-x-2">
                                  {editingDate === row.date ? (
                                    <>
                                      <button onClick={() => updateWeight(row.date)} className="p-2 bg-emerald-100 text-emerald-700 rounded-lg hover:bg-emerald-200"><Save className="w-3.5 h-3.5" /></button>
                                      <button onClick={() => setEditingDate(null)} className="p-2 bg-slate-100 text-slate-500 rounded-lg hover:bg-slate-200"><XCircle className="w-3.5 h-3.5" /></button>
                                    </>
                                  ) : (
                                    <>
                                      <button onClick={() => { setEditingDate(row.date); setEditWeight(row.weight_kg.toString()); }} className="p-2 text-slate-400 hover:text-blue-500 hover:bg-blue-50 rounded-lg transition-colors"><Edit3 className="w-3.5 h-3.5" /></button>
                                      <button onClick={() => deleteRecord(row.date)} className="p-2 text-slate-400 hover:text-rose-500 hover:bg-rose-50 rounded-lg transition-colors"><Trash2 className="w-3.5 h-3.5" /></button>
                                    </>
                                  )}
                                </td>
                             </tr>
                          ))}
                       </tbody>
                    </table>
                 </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}