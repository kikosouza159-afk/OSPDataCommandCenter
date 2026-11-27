/* SKY / Assistpay: PNG institucional 1920 x 1080, dados locais, sem CDN. */
(()=>{
'use strict';
const bgUrl=document.currentScript.dataset.background;
const $=s=>document.querySelector(s), all=(s,root=document)=>Array.from(root.querySelectorAll(s));
const txt=e=>(e?.textContent||'').replace(/\s+/g,' ').trim();
const C={navy:'#000049',blue:'#345F99',orange:'#FB5C28',green:'#087849',red:'#B82B34',ink:'#17243D',muted:'#526078',line:'#DCE3EC',light:'#F4F6FA'};
function font(c,s,w=400){c.font=w+' '+s+'px Arial, sans-serif'}
function text(c,v,x,y,max,s=22,color=C.ink,w=400,align='left',min=12){
 v=String(v??'—');font(c,s,w);while(c.measureText(v).width>max&&s>min)font(c,--s,w);
 if(c.measureText(v).width>max){while(v.length&&c.measureText(v+'…').width>max)v=v.slice(0,-1);v+='…'}
 c.fillStyle=color;c.textAlign=align;c.textBaseline='middle';c.fillText(v,x,y);
}
function box(c,x,y,w,h,fill='#fff',stroke=C.line,r=10){
 c.beginPath();c.roundRect(x,y,w,h,r);c.fillStyle=fill;c.fill();if(stroke){c.strokeStyle=stroke;c.lineWidth=1;c.stroke()}
}
function color(e){return e?.classList.contains('positive')?C.green:e?.classList.contains('negative')?C.red:C.muted}
const selected=(id)=>{const e=$(id);return txt(e?.querySelector('option[selected]')||e?.options?.[e.selectedIndex])};
const pct=v=>Number(v||0).toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2})+'%';
const classColor=n=>({Contato:C.blue,CPC:C.orange,Acordo:'#16834d'})[n]||'#8056bb';
function monthly(){
 const panels=all('.funnel-panel').map(p=>({
 title:txt(p.querySelector('h2')),days:txt(p.querySelector('.period-pill')),
 stages:all('.funnel-level',p).map(e=>({name:txt(e.querySelector('.stage-name')),value:txt(e.querySelector('.stage-value')),width:parseFloat(e.style.getPropertyValue('--stage-w'))||100})),
 delta:all('.variation-item',p).map(e=>({name:txt(e.querySelector('small')),value:txt(e.querySelector('strong')),color:color(e.querySelector('strong'))}))
 }));
 const table=$('.comparison-panel table');
 if(!table||!panels.length)throw Error('Não há dados para exportar.');
 return {panels,headers:all('thead th',table).map(txt),rows:all('tbody tr',table).map(r=>({cells:all('td',r).map(txt),color:color(r.querySelector('.compare-change'))})),
 subtitle:[selected('#anterior')+' × '+selected('#atual'),selected('#segmento'),($('#dias')?.defaultValue||'')+' dias trabalhados'].join('  |  ')};
}
function drawFunnel(c,p,x,y,w,h,i,compact){
 const accent=i?C.orange:C.blue;
 box(c,x,y,w,h,'#fff');
 text(c,p.title,x+20,y+30,w-40,compact?24:32,accent,700);
 text(c,p.days,x+20,y+60,w-40,19,C.muted);
 const start=y+91, gap=7, n=p.stages.length, step=Math.min(compact?57:76,(h-116)/Math.max(1,n));
 const deltaW=compact?120:185, content=w-deltaW-52;
 text(c,'Variação',x+w-20,y+77,deltaW,16,C.muted,700,'right');
 p.stages.forEach((s,j)=>{
 const yy=start+j*step,ww=content*s.width/100,xx=x+18+(content-ww)/2,hh=step-gap;
 c.beginPath();c.moveTo(xx,yy);c.lineTo(xx+ww,yy);c.lineTo(xx+ww-12,yy+hh);c.lineTo(xx+12,yy+hh);c.closePath();c.fillStyle=accent;c.fill();
 text(c,s.name,xx+17,yy+hh*.30,ww-34,compact?15:21,'#fff',700,'left',10);
 text(c,s.value,xx+ww-17,yy+hh*.73,ww-34,compact?21:29,'#fff',700,'right');
 const d=p.delta.find(d=>d.name.toLowerCase()===s.name.toLowerCase());
 if(d){box(c,x+w-deltaW-12,yy+2,deltaW,hh-4,C.light,C.line,6);text(c,d.value,x+w-deltaW/2-12,yy+hh/2,deltaW-10,compact?17:23,d.color,700,'center')}
 });
 const extras=p.delta.filter(d=>!p.stages.some(s=>s.name.toLowerCase()===d.name.toLowerCase()));
 if(extras.length){const yy=start+n*step+5;const eh=Math.min(30,(y+h-yy-10)/extras.length);if(eh>=12)extras.forEach((d,j)=>{text(c,d.name,x+20,yy+j*eh,w*.58,16,C.muted);text(c,d.value,x+w-20,yy+j*eh,w*.37,17,d.color,700,'right')})}
}
function drawTable(c,d,x,y,w,h,compact=false){
 box(c,x,y,w,h,'#fff');
 const xs=[x+16,x+w*.57,x+w*.78,x+w-16], ws=[w*.34,w*.20,w*.20,w*.18];
 box(c,x+8,y+8,w-16,43,C.navy,null,7);
 d.headers.forEach((v,j)=>text(c,v,xs[j],y+29,ws[j],compact?17:23,'#fff',700,j?'right':'left',10));
 const step=Math.min(45,(h-65)/Math.max(1,d.rows.length));
 d.rows.forEach((r,j)=>{const yy=y+57+j*step;if(j%2===0)box(c,x+8,yy,w-16,step,C.light,null,4);
 r.cells.forEach((v,k)=>text(c,v,xs[k],yy+step/2,ws[k],compact?17:23,k===3?r.color:k===1?C.blue:k===2?C.orange:C.ink,k?700:400,k?'right':'left',10))});
}
function monthlyPages(kind){
 const d=monthly();
 return [{title:kind==='funis'?'Funis de performance':kind==='indicadores'?'Visão comparativa dos indicadores':'Funis de performance e indicadores',
 sub:d.subtitle,foot:'Mailing exibido: média diária. Spin = Discado ÷ soma do Mailing. Pagamentos: valores exibidos após salvar.',
 draw(c){if(kind==='funis'){const w=850;d.panels.forEach((p,i)=>drawFunnel(c,p,95+i*880,233,w,727,i,false))}
 else if(kind==='indicadores'){drawTable(c,d,95,233,1730,727)}
 else{d.panels.forEach((p,i)=>drawFunnel(c,p,95+i*540,233,525,727,i,true));drawTable(c,d,1175,233,650,727,true)}}}];
}
function tabData(){
 const d=window.skySlideData;if(!d)throw Error('Dados de tabulação indisponíveis.');
 return d;
}
const chunks=(a,n)=>Array.from({length:Math.ceil(a.length/n)},(_,i)=>a.slice(i*n,(i+1)*n));
function classPages(index){
 const d=tabData(), groups=index===null?d.graficos:[d.graficos[index]];
 const pages=[];
 for(const g of groups.filter(Boolean)){
 const parts=chunks(g.etapas||[],15);
 parts.forEach((rows,p)=>pages.push({title:'Tabulações | '+g.classificacao,sub:d.sub+'  |  Média '+d.ref,
 foot:'Barras sólidas: período selecionado. Barras claras: média diária do mês. Escala fixa de 0% a 100%.',
 draw(c){const x=95,y=233,w=1730,h=727,accent=classColor(g.classificacao),sx=600,sw=980;
 box(c,x,y,w,h,'#fff');box(c,x+20,y+16,22,16,accent,null,3);text(c,'Período',x+53,y+24,190,20,C.ink,700);box(c,x+230,y+16,22,16,accent+'40',accent,3);text(c,'Média do mês',x+265,y+24,280,20,C.ink,700);
 for(let v=0;v<=100;v+=20){const xx=sx+sw*v/100;c.strokeStyle=C.line;c.beginPath();c.moveTo(xx,y+65);c.lineTo(xx,y+h-16);c.stroke();text(c,v+'%',xx,y+52,85,15,C.muted,400,'center')}
 const step=Math.min(65,635/rows.length);rows.forEach((r,j)=>{const yy=y+71+j*step;
 text(c,r.descricao||r.label,x+20,yy+step*.46,480,21,C.ink,700,'left',12);
 [r.percentual,r.media_mes].forEach((v,k)=>{const width=Math.max(0,Math.min(100,Number(v)||0))*sw/100,by=yy+3+k*(step/2),bh=Math.max(6,step/2-6);
 if(width>0)box(c,sx,by,width,bh,k?accent+'40':accent,k?accent:null,3);
 text(c,pct(v),sx+width+9,by+bh/2,135,17,C.ink,700,'left',12)})})}
 }))}
 return pages;
}
function heatPages(kind,index){
 const d=tabData(),hour=kind==='hora';
 const groups=hour?(d.visaoHora?.classificacoes||[]).filter(g=>g.classificacao===$('#hour-classification-filter')?.value):(index===null?d.evolucao:[d.evolucao[index]]);
 const pages=[];
 for(const g of groups.filter(Boolean)){
 const columns=hour?d.visaoHora.horas:g.dias;
 if(!columns?.length)continue;
 const rowGroups=chunks(g.etapas||[],22), colGroups=chunks(columns,20);
 rowGroups.forEach((rows,ri)=>colGroups.forEach((cols,ci)=>pages.push({
 title:(hour?'Tabulações por hora | ':'Heatmap diário | ')+g.classificacao,sub:(hour?d.sub:'Mês de referência: '+d.ref)+'  |  '+cols[0]+' a '+cols[cols.length-1],
 foot:hour?'Cada coluna representa 100% da classificação. Valores percentuais do período selecionado.':'Representatividade diária dentro de cada classificação. Intensidade da cor: 0% a 100%.',
 draw(c){const x=95,y=233,w=1730,h=727,accent=classColor(g.classificacao),left=420,cw=(w-left-22)/cols.length,rh=Math.min(43,650/rows.length);
 box(c,x,y,w,h,'#fff');
 box(c,x+10,y+10,w-20,45,C.navy,null,6);text(c,'Tabulação',x+22,y+32,left-30,21,'#fff',700);
 cols.forEach((v,j)=>text(c,v,x+left+(j+.5)*cw,y+32,cw-4,17,'#fff',700,'center',10));
 rows.forEach((r,j)=>{const yy=y+60+j*rh;text(c,r.descricao||r.label,x+20,yy+rh/2,left-28,19,C.ink,700,'left',11);
 cols.forEach((v,k)=>{const n=Number(r.valores?.[ci*20+k]||0),a=Math.round((.06+Math.min(100,Math.max(0,n))*.0094)*255).toString(16).padStart(2,'0');
 box(c,x+left+k*cw+1,yy+1,cw-2,rh-2,accent+a,null,3);text(c,pct(n),x+left+(k+.5)*cw,yy+rh/2,cw-4,16,n>65?'#fff':C.ink,700,'center',10)})})}
 })));
 }
 return pages;
}
let background;
async function createPNG(page,index,count){
 if(!background){const img=new Image();img.src=bgUrl;await img.decode();background=img}
 const canvas=document.createElement('canvas');canvas.width=1920;canvas.height=1080;const c=canvas.getContext('2d');
 c.drawImage(background,0,0,1920,1080);
 text(c,'SKY  /  ASSISTPAY  /  PERFORMANCE OPERACIONAL',95,126,1640,19,C.orange,700);
 text(c,page.title,95,169,1705,43,C.navy,700);
 text(c,page.sub,95,210,1705,21,C.muted);
 page.draw(c);text(c,page.foot,95,990,1690,18,C.muted);
 if(count>1)text(c,'Slide '+(index+1)+' de '+count,95,1019,1600,17,C.muted,700);
 const b=await new Promise((resolve,reject)=>canvas.toBlob(blob=>blob?resolve(blob):reject(Error('Falha na geração do PNG.')),'image/png'));
 return URL.createObjectURL(b);
}
function save(url,name){const a=document.createElement('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove()}
async function exportSlides(kind,index){
 const pages=kind==='classificacao'?classPages(index):kind==='hora'||kind==='heatmap'?heatPages(kind,index):monthlyPages(kind);
 if(!pages.length)throw Error('Não há dados para o filtro selecionado.');
 const name=(i)=>'SKY_'+kind+'_'+(i+1)+'.png';
 if(pages.length===1){const url=await createPNG(pages[0],0,1);save(url,name(0));setTimeout(()=>URL.revokeObjectURL(url),30000);return}
 const dialog=document.createElement('dialog');dialog.style.cssText='max-width:520px;width:90vw;border:1px solid #aeb9ca;border-radius:14px;background:#fff;color:#17243d;padding:24px;font:15px Arial';
 const title=document.createElement('h2');title.textContent='Exportar '+pages.length+' slides PNG';dialog.append(title);
 const note=document.createElement('p');note.textContent='Conteúdo dividido em slides para manter a legibilidade. Baixe cada imagem abaixo.';dialog.append(note);
 const list=document.createElement('div');list.style.cssText='display:grid;gap:8px;max-height:55vh;overflow:auto';dialog.append(list);
 pages.forEach((p,i)=>{const b=document.createElement('button');b.type='button';b.textContent='↓ '+(i+1)+' · '+p.title;b.style.cssText='padding:12px;text-align:left;border:1px solid #dce3ec;border-radius:8px;background:#f4f6fa;color:#000049;cursor:pointer';b.onclick=async()=>{b.disabled=true;try{const url=await createPNG(p,i,pages.length);save(url,name(i));setTimeout(()=>URL.revokeObjectURL(url),30000)}catch(e){alert(e.message)}finally{b.disabled=false}};list.append(b)});
 const close=document.createElement('button');close.textContent='Fechar';close.style.cssText='margin-top:16px;padding:10px 20px;background:#000049;color:#fff;border:0;border-radius:8px;cursor:pointer';close.onclick=()=>dialog.close();dialog.append(close);dialog.addEventListener('close',()=>dialog.remove(),{once:true});document.body.append(dialog);dialog.showModal();
}
all('[data-sky-slide]').forEach(b=>b.addEventListener('click',async()=>{const old=b.textContent;b.disabled=true;b.textContent='Gerando…';try{await exportSlides(b.dataset.skySlide,b.dataset.skyIndex===undefined?null:Number(b.dataset.skyIndex))}catch(e){console.error(e);alert('Não foi possível exportar: '+e.message)}finally{b.disabled=false;b.textContent=old}}));
})();