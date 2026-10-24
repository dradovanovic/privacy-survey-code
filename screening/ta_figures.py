"""Title/abstract figures for Stream A (screening_spec.md section 7). Run from code/data/screening/."""
import csv,glob,math,collections
def wilson(k,n,z=1.96):
    if n==0: return (float('nan'),)*3
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return p,c-h,c+h
def kappa(pairs):
    N=len(pairs);a=sum(1 for x,y in pairs if x==y=='retain');d=sum(1 for x,y in pairs if x==y=='exclude')
    p1=sum(1 for x,_ in pairs if x=='retain')/N;p2=sum(1 for _,y in pairs if y=='retain')/N
    po=(a+d)/N;pe=p1*p2+(1-p1)*(1-p2);return (po-pe)/(1-pe),po,p1,p2
rows=[];per=[]
for f in sorted(glob.glob('stream-a-v1.batch??.compare.csv')):
    R=list(csv.DictReader(open(f,encoding='utf-8-sig'),delimiter=';')); b=int(f[17:19]); rows+= [dict(r,batch=b) for r in R]
ret=lambda d:'retain' if d in('include','maybe') else 'exclude'
print('records',len(rows),'ns',min(int(r['n']) for r in rows),max(int(r['n']) for r in rows),'empty ta_final',sum(not r['ta_final'] for r in rows))
E7=[r for r in rows if r['ta_agreement']=='A-E7']; R=[r for r in rows if r['ta_agreement']!='A-E7']
print('A-E7',len(E7),'LLM on A-E7 votes',collections.Counter(r['llm_vote'] for r in E7))
print('analysed',len(R))
print('H1 decisions',collections.Counter(r['h1_ta_decision'] for r in R),'LLM run1',collections.Counter(r['llm_run1'] for r in R),'run2',collections.Counter(r['llm_run2'] for r in R))
print('ta_final',collections.Counter(r['ta_final'] for r in rows),'(analysed)',collections.Counter(r['ta_final'] for r in R))
def sens_spec(ref,test,lab):
    tp=sum(1 for r in R if ref(r)=='retain' and test(r)=='retain');fn=sum(1 for r in R if ref(r)=='retain' and test(r)=='exclude')
    tn=sum(1 for r in R if ref(r)=='exclude' and test(r)=='exclude');fp=sum(1 for r in R if ref(r)=='exclude' and test(r)=='retain')
    s=wilson(tp,tp+fn);sp=wilson(tn,tn+fp)
    print(f"{lab}: TP {tp} FN {fn} TN {tn} FP {fp} | sens {s[0]:.3f} [{s[1]:.3f},{s[2]:.3f}] | spec {sp[0]:.3f} [{sp[1]:.3f},{sp[2]:.3f}]")
sens_spec(lambda r:r['ta_final'],lambda r:r['llm_vote'],'LLM vs ta_final')
sens_spec(lambda r:r['h1_vote'],lambda r:r['llm_vote'],'LLM vs H1 blind')
sens_spec(lambda r:r['ta_final'],lambda r:r['h1_vote'],'H1 blind vs ta_final')
sens_spec(lambda r:r['ta_final'],lambda r:ret(r['llm_run1']),'LLM run1 alone vs ta_final')
sens_spec(lambda r:r['ta_final'],lambda r:ret(r['llm_run2']),'LLM run2 alone vs ta_final')
k,po,p1,p2=kappa([(r['h1_vote'],r['llm_vote']) for r in R]);print(f"kappa H1-LLM {k:.3f} po {po:.3f} prev H1 {p1:.3f} LLM {p2:.3f}")
# disagreements
d1=[r for r in R if r['h1_vote']=='exclude' and r['llm_vote']=='retain'];d2=[r for r in R if r['h1_vote']=='retain' and r['llm_vote']=='exclude']
print('disagree H1excl/LLMret',len(d1),'-> final retain',sum(r['ta_final']=='retain' for r in d1),'| H1ret/LLMexcl',len(d2),'-> final exclude',sum(r['ta_final']=='exclude' for r in d2))
print('H1 changed overall',sum(r['ta_final']!=r['h1_vote'] for r in R),'agreements changed',sum(1 for r in R if r['ta_agreement']=='agree' and r['ta_final']!=r['h1_vote']))
print('LLM-only retains (H1 excl, LLM ret, final ret):',[r['n'] for r in d1 if r['ta_final']=='retain'])
# run-to-run
k2,po2,a,b=kappa([(ret(r['llm_run1']),ret(r['llm_run2'])) for r in R])
print(f"run-run exact {sum(r['llm_run1']==r['llm_run2'] for r in R)}/{len(R)} retexcl {sum(ret(r['llm_run1'])==ret(r['llm_run2']) for r in R)}/{len(R)} kappa {k2:.3f}")
print('LLM decision split pattern',collections.Counter(tuple(sorted((r['llm_run1'],r['llm_run2']))) for r in R if r['llm_run1']!=r['llm_run2']))
# per batch
print('batch N agree kappa H1ret LLMret final_ret')
for b in range(1,18):
    B=[r for r in R if r['batch']==b]; k,po,p1,p2=kappa([(r['h1_vote'],r['llm_vote']) for r in B])
    print(b,len(B),sum(r['h1_vote']==r['llm_vote'] for r in B),round(k,2),sum(r['h1_vote']=='retain' for r in B),sum(r['llm_vote']=='retain' for r in B),sum(r['ta_final']=='retain' for r in B))
# H1 sensitivity value
print('records H1 excluded but final retain:',sum(1 for r in R if r['h1_vote']=='exclude' and r['ta_final']=='retain'))
# exclusion code distribution of final excludes (primary code of reason or h1 code)
import re
def code(r):
    m=re.match(r'\s*(A-E\d)',r['ta_final_reason']); 
    return m.group(1) if m else (re.match(r'(A-E\d)',r['h1_ta_codes']).group(1) if re.match(r'(A-E\d)',r['h1_ta_codes']) else '?')
print('final exclude codes',collections.Counter(code(r) for r in rows if r['ta_final']=='exclude'))
