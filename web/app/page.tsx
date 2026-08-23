import Link from 'next/link';

const FEATURES = [
  ['✓','ATS Match Score','See how closely your resume aligns to a specific job description.'],
  ['⌕','Keyword Analysis','Find matched and missing keywords before you apply.'],
  ['↗','Detailed Insights','Understand strengths, gaps and recruiter-style concerns.'],
  ['✦','Smart Suggestions','Get practical, evidence-based improvements without inventing experience.'],
  ['⇩','Saved Reports','Keep a history of analyses in the test workspace.'],
  ['🔒','Privacy First','API keys stay on the server and resumes are not stored by the app server.']
];

export default function Home(){
  return <main>
    <header className="topbar">
      <div className="brand"><span className="logo">⌕</span><span>Smart <b style={{color:'var(--primary)'}}>ATS</b><small style={{display:'block',fontSize:11,fontWeight:500}}>Analyzer</small></span></div>
      <nav className="nav"><a href="#features">Features</a><a href="#how">How It Works</a><a href="#pricing">Pricing</a><a href="#faq">FAQ</a></nav>
      <div className="actions"><Link className="btn btn-light" href="/dashboard">Demo</Link><Link className="btn btn-primary" href="/dashboard">Start Free Analysis →</Link></div>
    </header>

    <section className="hero">
      <div className="container hero-grid">
        <div>
          <span className="eyebrow">✦ AI-powered · Job-specific · Actionable</span>
          <h1>Know Your Resume Match <span>Before You Apply.</span></h1>
          <p>Compare your resume with any job description and see the keywords, skills and gaps that may matter before you send your application.</p>
          <div className="chips"><span className="chip">✓ Save time</span><span className="chip">✓ Spot missing keywords</span><span className="chip">✓ Improve job alignment</span></div>
          <div className="actions"><Link className="btn btn-primary" href="/dashboard">Start Free Analysis →</Link><a className="btn btn-light" href="#features">See Features</a></div>
          <p style={{fontSize:12,marginTop:16}}>Test mode includes 10 analysis credits. No login required.</p>
        </div>
        <div className="preview">
          <div className="score-row">
            <div className="score-circle"><div className="score-inner"><strong>78%</strong><div style={{color:'var(--green)',fontSize:12}}>Good Match</div></div></div>
            <div>
              {[['Skills Match',82],['Keywords Match',69],['Experience Match',77],['ATS Readability',65]].map(([label,value])=><div className="metric" key={String(label)}><div className="metric-head"><span>{label}</span><b>{value}%</b></div><div className="bar"><i style={{width:`${value}%`}}/></div></div>)}
            </div>
          </div>
          <div className="notice"><b>Top missing keywords:</b> Kubernetes · Docker · AWS · CI/CD · Redis</div>
          <div style={{marginTop:14}}><b>✦ AI Insight</b><p className="muted" style={{fontSize:13}}>Prioritize missing must-have skills only when they are genuinely supported by your experience.</p></div>
        </div>
      </div>
      <div className="container trust-strip">
        <div className="trust"><strong>10</strong><small>Free test credits</small></div>
        <div className="trust"><strong>1</strong><small>Credit per successful analysis</small></div>
        <div className="trust"><strong>₹99</strong><small>Planned starter pack</small></div>
        <div className="trust"><strong>Private</strong><small>Server-side API key</small></div>
      </div>
      <p className="container" style={{fontSize:11,color:'var(--muted)',marginTop:10}}>Social-proof figures such as “1,000+ applicants” and “50+ HRs” should only be enabled publicly after they are verified.</p>
    </section>

    <section id="features" className="section container"><span className="eyebrow" style={{display:'table',margin:'0 auto 12px'}}>Why Smart ATS?</span><h2>Everything you need before applying</h2><p className="section-sub">A focused MVP around one job: compare, understand, improve.</p><div className="feature-grid">{FEATURES.map(([icon,title,desc])=><div className="card feature" key={title}><div className="feature-icon">{icon}</div><b>{title}</b><p>{desc}</p></div>)}</div></section>

    <section id="how" className="section" style={{background:'#f3f1ff'}}><div className="container"><h2>How it works</h2><p className="section-sub">Simple, fast, job-specific.</p><div className="steps">{[['Upload Resume','PDF or DOCX'],['Paste Job Description','Use the complete JD'],['AI Analysis','Fixed model, no model picker'],['Get Your Report','Score, gaps and recommendations']].map((s,i)=><div className="card step" key={s[0]}><div className="step-no">{i+1}</div><b>{s[0]}</b><p className="muted">{s[1]}</p></div>)}</div></div></section>

    <section id="pricing" className="pricing"><div className="container" style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:30,alignItems:'center'}}><div><h2 style={{textAlign:'left',fontSize:36}}>Ready to test your resume against the next job?</h2><p>Use the MVP free first. The intended paid starter pack is 10 analyses for ₹99 after payment integration and validation.</p></div><div className="price-card"><span className="pill good">Planned Starter Pack</span><div style={{marginTop:12}}><b>10 analyses</b><div className="price">₹99</div><p className="muted">One-time credit purchase · no subscription required.</p><Link className="btn btn-primary" style={{display:'block',textAlign:'center'}} href="/dashboard">Test MVP Now →</Link></div></div></div></section>

    <section id="faq" className="section container"><h2>Frequently asked questions</h2><div className="card" style={{padding:24,maxWidth:850,margin:'28px auto'}}><div className="faq"><b>Is this an official ATS vendor score?</b><p className="muted">No. It is an AI-assisted resume-to-JD alignment estimate designed to help applicants improve before applying.</p></div><div className="faq"><b>Which model is used?</b><p className="muted">The model is fixed by the server configuration. Users cannot select or manipulate the model.</p></div><div className="faq"><b>What happens after 10 credits?</b><p className="muted">The test workspace blocks further analyses and shows a recharge prompt. Payments are intentionally not connected yet.</p></div></div></section>
    <footer className="footer"><span>© 2026 Smart ATS Analyzer</span><span>Privacy · Terms · Refund Policy · Contact</span></footer>
  </main>
}
