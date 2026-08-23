'use client';

import Link from 'next/link';
import { FormEvent, useEffect, useMemo, useState } from 'react';

type Analysis = {
  id: string;
  jobTitle: string;
  company: string;
  createdAt: string;
  match_score: number;
  match_level: string;
  matched_keywords: string[];
  missing_keywords: string[];
  strengths: string[];
  gaps: string[];
  profile_summary: string;
  recommendations: string[];
  recruiter_verdict: string;
};

type View = 'Dashboard'|'My Analyses'|'My Profile'|'Billing & Credits'|'Help & Support';

const STARTING_CREDITS = 10;
const STORAGE_CREDITS = 'smart-ats-demo-credits-v1';
const STORAGE_HISTORY = 'smart-ats-demo-history-v1';

function scoreClass(score:number){return score>=80?'good':score>=50?'warn':'bad'}
function level(score:number){return score>=85?'Excellent':score>=70?'Strong':score>=50?'Moderate':'Low'}

export default function DashboardPage(){
  const [view,setView]=useState<View>('Dashboard');
  const [credits,setCredits]=useState(STARTING_CREDITS);
  const [history,setHistory]=useState<Analysis[]>([]);
  const [jd,setJd]=useState('');
  const [file,setFile]=useState<File|null>(null);
  const [jobTitle,setJobTitle]=useState('');
  const [company,setCompany]=useState('');
  const [loading,setLoading]=useState(false);
  const [error,setError]=useState('');
  const [result,setResult]=useState<Analysis|null>(null);
  const [hydrated,setHydrated]=useState(false);

  useEffect(()=>{
    const c=localStorage.getItem(STORAGE_CREDITS);
    const h=localStorage.getItem(STORAGE_HISTORY);
    if(c!==null) setCredits(Math.max(0,Math.min(STARTING_CREDITS,Number(c))));
    if(h){try{setHistory(JSON.parse(h))}catch{}}
    setHydrated(true);
  },[]);

  useEffect(()=>{if(hydrated)localStorage.setItem(STORAGE_CREDITS,String(credits))},[credits,hydrated]);
  useEffect(()=>{if(hydrated)localStorage.setItem(STORAGE_HISTORY,JSON.stringify(history))},[history,hydrated]);

  async function analyze(e:FormEvent){
    e.preventDefault(); setError('');
    if(credits<=0){setError('You have used all 10 test credits. Recharge will be available after payment integration.');return}
    if(!file||!jd.trim()){setError('Upload a resume and paste the complete job description.');return}
    setLoading(true);
    try{
      const form=new FormData(); form.append('resume',file); form.append('jobDescription',jd); form.append('jobTitle',jobTitle); form.append('company',company);
      const res=await fetch('/api/analyze',{method:'POST',body:form});
      const data=await res.json();
      if(!res.ok) throw new Error(data.error||'Analysis failed');
      const item:Analysis={id:crypto.randomUUID(),jobTitle:jobTitle||'Untitled role',company:company||'Unknown company',createdAt:new Date().toISOString(),...data};
      setResult(item); setHistory(prev=>[item,...prev].slice(0,50)); setCredits(c=>Math.max(0,c-1));
    }catch(err){setError(err instanceof Error?err.message:'Analysis failed')}
    finally{setLoading(false)}
  }

  function resetDemo(){localStorage.removeItem(STORAGE_CREDITS);localStorage.removeItem(STORAGE_HISTORY);setCredits(STARTING_CREDITS);setHistory([]);setResult(null);setError('')}
  const avg=useMemo(()=>history.length?Math.round(history.reduce((a,b)=>a+b.match_score,0)/history.length):0,[history]);

  return <div className="app-shell">
    <aside className="sidebar">
      <Link href="/" className="brand side-brand"><span className="logo">⌕</span><span>Smart <b style={{color:'var(--primary)'}}>ATS</b><small style={{display:'block',fontSize:11,fontWeight:500}}>Analyzer</small></span></Link>
      <div className="menu">{(['Dashboard','My Analyses','My Profile','Billing & Credits','Help & Support'] as View[]).map(item=><button key={item} className={view===item?'active':''} onClick={()=>setView(item)}>{item==='Dashboard'?'⌂':item==='My Analyses'?'◴':item==='My Profile'?'♙':item==='Billing & Credits'?'▣':'?'} &nbsp; {item}</button>)}</div>
      <div className="credit-card"><div>⚡ Credits Left</div><strong>{credits} / 10</strong><div className="bar"><i style={{width:`${credits*10}%`,background:'var(--primary)'}}/></div><p className="muted" style={{fontSize:12}}>Each successful analysis uses 1 credit.</p><button className="btn btn-primary" style={{width:'100%'}} onClick={()=>setView('Billing & Credits')}>{credits?'View Credits':'Recharge Credits'}</button></div>
      <button onClick={resetDemo} className="btn btn-light" style={{width:'100%',marginTop:12,fontSize:12}}>Reset test data</button>
    </aside>

    <main className="app-main">
      <header className="app-header"><span className="pill warn">⚡ Credits Left &nbsp; {credits} / 10</span><span>🔔</span><span className="logo" style={{width:34,height:34,fontSize:13}}>AD</span></header>
      {view==='Dashboard'&&<Dashboard credits={credits} jd={jd} setJd={setJd} file={file} setFile={setFile} jobTitle={jobTitle} setJobTitle={setJobTitle} company={company} setCompany={setCompany} loading={loading} error={error} analyze={analyze} result={result} setResult={setResult} setView={setView}/>} 
      {view==='My Analyses'&&<Analyses history={history} onOpen={a=>{setResult(a);setView('Dashboard')}}/>}
      {view==='My Profile'&&<Profile credits={credits} total={history.length} avg={avg}/>} 
      {view==='Billing & Credits'&&<Billing credits={credits}/>} 
      {view==='Help & Support'&&<Help/>}
    </main>
  </div>
}

function Dashboard(p:any){return <section className="page">
  <p className="mobile-note notice">Desktop navigation collapses on small screens in this MVP.</p>
  {!p.result?<>
    <h1 className="page-title">Resume Match Dashboard</h1><p className="page-sub">Upload a resume, paste the job description and get a focused match report.</p>
    {p.credits===0&&<div className="notice" style={{background:'#fff0f0',color:'#b42318'}}>You’ve used all 10 test credits. Further analyses are blocked. Open Billing & Credits to see the planned recharge flow.</div>}
    <form className="analysis-grid" onSubmit={p.analyze}>
      <div className="card panel"><label className="label">Job title (optional)</label><input className="input" value={p.jobTitle} onChange={(e:any)=>p.setJobTitle(e.target.value)} placeholder="AI Engineer"/><label className="label" style={{marginTop:14}}>Company (optional)</label><input className="input" value={p.company} onChange={(e:any)=>p.setCompany(e.target.value)} placeholder="Company name"/><label className="label" style={{marginTop:14}}>Job description</label><textarea className="textarea" value={p.jd} onChange={(e:any)=>p.setJd(e.target.value)} placeholder="Paste the complete job description…"/><div className="muted" style={{fontSize:12,marginTop:7}}>{p.jd.length.toLocaleString()} characters</div></div>
      <div className="card panel"><label className="label">Resume</label><label className="upload"><div style={{fontSize:34}}>⇧</div><b>{p.file?p.file.name:'Upload PDF or DOCX'}</b><p className="muted">Text-based PDF or DOCX · max 5 MB</p><input type="file" accept=".pdf,.docx" hidden onChange={(e:any)=>p.setFile(e.target.files?.[0]||null)}/></label><div className="notice"><b>Before analyzing</b><br/>Use the complete JD. Keep resume claims truthful. A successful analysis consumes 1 credit; failed requests do not.</div>{p.error&&<div className="notice" style={{background:'#fff0f0',color:'#b42318'}}>{p.error}</div>}<button className="btn btn-primary" disabled={p.loading||p.credits<=0} style={{width:'100%',marginTop:16,opacity:p.loading||p.credits<=0?.6:1}}>{p.loading?'Analyzing…':'Analyze Resume →'}</button></div>
    </form>
  </>:<Report result={p.result} onNew={()=>p.setResult(null)} credits={p.credits}/>} 
</section>}

function Report({result,onNew,credits}:{result:Analysis,onNew:()=>void,credits:number}){return <>
  <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',gap:16}}><div><h1 className="page-title">Analysis Report</h1><p className="page-sub">Here’s how well your resume matches this job description.</p></div><button className="btn btn-primary" onClick={onNew}>＋ New Analysis</button></div>
  <div className="result-top"><div className="card panel" style={{textAlign:'center'}}><b>ATS Match Score</b><div className="score-circle" style={{margin:'18px auto'}}><div className="score-inner"><strong>{result.match_score}%</strong><div className={scoreClass(result.match_score)}>{level(result.match_score)} Match</div></div></div><p className="muted">AI-estimated resume/JD alignment, not an official vendor ATS score.</p></div><div className="card panel"><div className="stats"><div className="card stat"><span>Match</span><strong>{result.match_score}%</strong></div><div className="card stat"><span>Matched</span><strong>{result.matched_keywords.length}</strong></div><div className="card stat"><span>Missing</span><strong>{result.missing_keywords.length}</strong></div><div className="card stat"><span>Credits left</span><strong>{credits}</strong></div></div><div className="notice" style={{marginTop:18}}><b>Recruiter verdict:</b> {result.recruiter_verdict}</div></div></div>
  <div className="columns3"><div className="card panel"><b>✓ Matched Keywords</b><div className="tag-list" style={{marginTop:14}}>{result.matched_keywords.map(x=><span className="tag" key={x}>{x}</span>)}</div></div><div className="card panel"><b>⊗ Missing Keywords</b><div className="tag-list" style={{marginTop:14}}>{result.missing_keywords.map(x=><span className="tag missing" key={x}>{x}</span>)}</div></div><div className="card panel"><b>Top Strengths</b><ul className="list">{result.strengths.map(x=><li key={x}>{x}</li>)}</ul></div></div>
  <div className="profile-grid"><div className="card panel"><b>Areas to improve</b><ul className="list">{result.gaps.map(x=><li key={x}>{x}</li>)}</ul></div><div className="card panel"><b>Tailored Summary</b><p className="muted" style={{lineHeight:1.7}}>{result.profile_summary}</p></div></div>
  <div className="card panel" style={{marginTop:18}}><b>✦ AI Recommendations</b><ol className="list">{result.recommendations.map(x=><li key={x}>{x}</li>)}</ol></div>
</>}

function Analyses({history,onOpen}:{history:Analysis[],onOpen:(a:Analysis)=>void}){const [q,setQ]=useState('');const rows=history.filter(x=>(x.jobTitle+' '+x.company).toLowerCase().includes(q.toLowerCase()));return <section className="page"><h1 className="page-title">My Analyses</h1><p className="page-sub">View your past resume analyses and reopen their reports.</p><div className="card panel" style={{marginTop:22}}><input className="input" placeholder="Search by job title or company…" value={q} onChange={e=>setQ(e.target.value)}/><div className="table-wrap" style={{marginTop:14}}>{rows.length?<table className="table"><thead><tr><th>Job Title</th><th>Company</th><th>Score</th><th>Analyzed On</th><th>Credits</th><th>Action</th></tr></thead><tbody>{rows.map(a=><tr key={a.id}><td><b>{a.jobTitle}</b></td><td>{a.company}</td><td><span className={`pill ${scoreClass(a.match_score)}`}>{a.match_score}% · {level(a.match_score)}</span></td><td>{new Date(a.createdAt).toLocaleString()}</td><td>1</td><td><button className="btn btn-light" onClick={()=>onOpen(a)}>Open</button></td></tr>)}</tbody></table>:<div className="empty">No analyses yet. Run your first resume match from Dashboard.</div>}</div></div></section>}

function Profile({credits,total,avg}:{credits:number,total:number,avg:number}){return <section className="page"><h1 className="page-title">My Profile</h1><p className="page-sub">Demo account for MVP testing. Google sign-in comes in the production auth phase.</p><div className="profile-grid"><div><div className="card panel"><div style={{display:'flex',gap:18,alignItems:'center'}}><span className="logo" style={{width:72,height:72,fontSize:26}}>AD</span><div><h2 style={{margin:0}}>Aman Demo</h2><p className="muted">demo@smartats.local</p><span className="pill good">Test Account</span></div></div></div><div className="card panel" style={{marginTop:18}}><b>Account Information</b><div className="setting-row"><span>Full Name</span><b>Aman Demo</b></div><div className="setting-row"><span>Email</span><b>demo@smartats.local</b></div><div className="setting-row"><span>Authentication</span><b>Skipped in test mode</b></div></div></div><div><div className="card panel"><b>Usage Overview</b><div className="stats" style={{marginTop:14}}><div className="card stat"><span>Total</span><strong>{total}</strong></div><div className="card stat"><span>Average</span><strong>{avg}%</strong></div><div className="card stat"><span>Used</span><strong>{10-credits}</strong></div><div className="card stat"><span>Left</span><strong>{credits}</strong></div></div></div><div className="card panel" style={{marginTop:18}}><b>Production roadmap</b><ul className="list"><li>Google OAuth through Supabase</li><li>Per-user server-side credits</li><li>Encrypted analysis history</li><li>Account deletion/export controls</li></ul></div></div></div></section>}

function Billing({credits}:{credits:number}){return <section className="page"><h1 className="page-title">Billing & Credits</h1><p className="page-sub">Recharge is mocked for the MVP. No payment is taken yet.</p><div className="billing-grid"><div className="card panel"><b>Credits Overview</b><div style={{fontSize:46,fontWeight:800,color:'var(--primary)',margin:'24px 0'}}>{credits} / 10</div><div className="bar"><i style={{width:`${credits*10}%`,background:'var(--primary)'}}/></div><p className="muted">Each successful resume analysis consumes one credit.</p></div><div className="card panel"><b>Choose a Plan</b><div className="plan-grid" style={{marginTop:16}}><div className="plan featured"><b>Starter</b><h2>10 credits</h2><div className="price" style={{fontSize:30}}>₹99</div><p className="muted">Planned MVP launch price.</p><button className="btn btn-primary" onClick={()=>alert('Payments are disabled in test mode.')}>Recharge</button></div><div className="plan"><b>Pro</b><h2>25 credits</h2><div className="price" style={{fontSize:30}}>₹199</div><p className="muted">Planned later.</p></div><div className="plan"><b>Premium</b><h2>50 credits</h2><div className="price" style={{fontSize:30}}>₹349</div><p className="muted">Planned later.</p></div></div></div></div><div className="notice">Production phase: Razorpay order creation, webhook verification, server-side wallet ledger, invoices and refund handling.</div></section>}

function Help(){const qs=[['How is the ATS score calculated?','It is an AI-assisted estimate based on resume/JD evidence, keywords, requirements and role alignment. It is not a vendor-specific ATS score.'],['What file formats are supported?','The Next.js MVP accepts text-based PDF and DOCX resumes.'],['How do credits work?','One credit is deducted only after a successful analysis. Test mode starts with 10 credits in your browser.'],['What happens when credits reach zero?','New analyses are blocked and the app shows a recharge prompt. Payment is intentionally disabled for MVP testing.'],['Is my API key exposed?','No. The OpenAI key is read only in the server API route, never sent to the browser.']];return <section className="page"><h1 className="page-title">Help & Support</h1><p className="page-sub">Answers for the MVP and a clear route to support.</p><div className="support-grid"><div className="card panel"><b>Frequently Asked Questions</b>{qs.map(([q,a])=><details className="faq" key={q}><summary><b>{q}</b></summary><p className="muted">{a}</p></details>)}</div><div><div className="card panel"><h3>Contact Support</h3><p className="muted">For the first beta, route support to your preferred email/WhatsApp after you decide the public contact details.</p><button className="btn btn-primary" onClick={()=>alert('Add your support email before public launch.')}>Contact Support</button></div><div className="card panel" style={{marginTop:18}}><h3>Guides & Tutorials</h3><ul className="list"><li>Getting started with Smart ATS</li><li>Understanding your match report</li><li>Resume optimization without keyword stuffing</li><li>How credits and recharge work</li></ul></div></div></div></section>}
