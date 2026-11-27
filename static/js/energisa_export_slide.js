/* Energisa: exportação PNG 16:9, sem dependências externas. */
(() => {
  'use strict';
  const script = document.currentScript;
  const bgUrl = script.dataset.background;
  const $ = id => document.getElementById(id);
  const text = el => (el?.textContent || '').replace(/\s+/g, ' ').trim();
  const t = id => text($(id));
  const all = (id, selector) => Array.from($(id)?.querySelectorAll(selector) || []);
  const colors = { navy:'#000049', blue:'#345F99', orange:'#FB5C28', ink:'#16233d', muted:'#536078', line:'#dbe1e9', green:'#087849', red:'#b82b34' };
  const font = (ctx, size, weight=400) => { ctx.font = weight + ' ' + size + 'px Arial, sans-serif'; };
  function label(ctx, str, x, y, width, size=22, color=colors.ink, weight=400, align='left', min=14) {
    str = String(str || '—');
    ctx.fillStyle=color; ctx.textAlign=align; ctx.textBaseline='middle';
    font(ctx,size,weight);
    while(ctx.measureText(str).width>width && size>min) font(ctx,--size,weight);
    if(ctx.measureText(str).width>width) {
      while(str.length && ctx.measureText(str+'…').width>width) str=str.slice(0,-1);
      str+='…';
    }
    ctx.fillText(str,x,y);
  }
  function rect(ctx,x,y,w,h,fill,stroke,rad=12) {
    ctx.beginPath(); ctx.roundRect(x,y,w,h,rad); ctx.fillStyle=fill; ctx.fill();
    if(stroke) {ctx.strokeStyle=stroke;ctx.lineWidth=1;ctx.stroke();}
  }
  function deltaColor(el) {
    return el?.classList.contains('up') || el?.classList.contains('pos') ? colors.green :
      el?.classList.contains('down') || el?.classList.contains('neg') ? colors.red : colors.muted;
  }
  function snapshot() {
    const sides=['AD','ADA'].map((key,i)=>{
      const name=t('funnelType'+key)||key;
      const campaign=t('funnelCampaign'+key);
      const deltaRoot=$('funnelDeltas'+key);
      const deltas=all('funnelDeltas'+key,'.assist-funnel-delta-item strong');
      const metrics=id=>all(id,'.assist-mini-metric').map(el=>({
        label:text(el.querySelector('span')), value:text(el.querySelector('b'))
      }));
      return {name, campaign, period:t('funnelPeriod'+key), days:t('funnelDays'+key),
        agents:text($('funnelAgents'+key)?.querySelector('strong')),
        color:i?colors.orange:colors.blue,
        deltaTitle:text(deltaRoot?.querySelector('.assist-delta-sub')) || 'Variação',
        stages:all('funnel'+key,'.assist-funnel-stage').map((el,j)=>({
          label:text(el.querySelector('.assist-stage-label')).replace(/classificação/i,'').trim(),
          value:text(el.querySelector('.assist-stage-value')),
          width:parseFloat(el.style.getPropertyValue('--funnel-width'))||100,
          delta:text(deltas[j]), deltaColor:deltaColor(deltas[j])
        })),
        rates:metrics('funnelRates'+key), productivity:metrics('funnelAGV'+key)};
    });
    const rows=all('comparisonBody','tr').map(row=>{
      const cells=Array.from(row.cells);
      return {group:cells.length===1, cells:cells.map(text), color:deltaColor(cells[3]),
        highlight:row.classList.contains('assist-row-highlight')};
    });
    if(sides.some(side=>!side.stages.length) || !rows.length) throw Error('Aguarde o carregamento dos indicadores.');
    return {sides,rows,mode:$('btnTotal')?.getAttribute('aria-pressed')==='true'?'Total':'Média dia',
      comparison:text(document.querySelector('.assist-panel-table .assist-panel-title p'))};
  }
  function metricGrid(ctx,items,x,y,w,title) {
    label(ctx,title,x,y+10,w,20,colors.navy,700);
    const cols=3, gap=9, cell=(w-gap*(cols-1))/cols;
    items.forEach((item,i)=>{
      const xx=x+(i%cols)*(cell+gap), yy=y+25+Math.floor(i/cols)*37;
      rect(ctx,xx,yy,cell,33,'#f4f6fa',colors.line,7);
      label(ctx,item.label,xx+9,yy+9,cell-18,13,colors.muted,400,'left',10);
      label(ctx,item.value,xx+9,yy+24,cell-18,18,colors.ink,700,'left',12);
    });
    return y+25+Math.ceil(items.length/cols)*37;
  }
  function drawFunnels(ctx,data) {
    const x0=95, w=850, y=233;
    data.sides.forEach((s,i)=>{
      const x=x0+i*880;
      rect(ctx,x,y,w,727,'#ffffff',colors.line,18);
      rect(ctx,x+18,y+18,7,68,s.color,null,3);
      label(ctx,'Funil '+s.name,x+37,y+36,w-65,32,s.color,700);
      label(ctx,s.period+'  ·  '+s.days,x+37,y+68,w-65,22,colors.muted);
      label(ctx,s.campaign,x+25,y+103,w-50,21,colors.ink,700,'left',14);
      label(ctx,'Agentes (média dia): '+s.agents,x+25,y+132,w-50,20,colors.muted,700);
      label(ctx,s.deltaTitle,x+w-26,y+157,210,17,colors.muted,700,'right');
      s.stages.forEach((stage,j)=>{
        const yy=y+171+j*43, ww=600*stage.width/100, xx=x+25+(600-ww)/2;
        ctx.beginPath();ctx.moveTo(xx,yy);ctx.lineTo(xx+ww,yy);ctx.lineTo(xx+ww-13,yy+38);ctx.lineTo(xx+13,yy+38);ctx.closePath();
        ctx.fillStyle=s.color;ctx.fill();
        label(ctx,stage.label,xx+24,yy+19,ww*.48-24,19,'#fff',700,'left',12);
        label(ctx,stage.value,xx+ww-24,yy+19,ww*.48-24,25,'#fff',700,'right',15);
        rect(ctx,x+w-191,yy+2,166,34,'#f4f6fa',colors.line,7);
        label(ctx,stage.delta,x+w-108,yy+19,150,21,stage.deltaColor,700,'center',13);
      });
      const end=metricGrid(ctx,s.rates,x+25,y+477,w-50,'Taxas e eficiência');
      metricGrid(ctx,s.productivity,x+25,end+4,w-50,'Produtividade por agente');
    });
    label(ctx,'Mailing: média diária sem zeros. VoiceMail integra o CPC e não deve ser somado novamente. CPC Líquido = CPC − VoiceMail.',95,985,1705,18,colors.muted);
    label(ctx,'Conversão = Acordos ÷ CPC Líquido. Crescimento de VoiceMail é favorável na regra Energisa.',95,1011,1705,18,colors.muted);
  }
  function drawTable(ctx,data) {
    const split=data.rows.findIndex(row=>row.group && /taxas/i.test(row.cells[0]));
    const at=split>0?split:Math.ceil(data.rows.length/2);
    const blocks=[data.rows.slice(0,at),data.rows.slice(at)];
    const w=850, x0=95,y=233;
    blocks.forEach((rows,i)=>{
      const x=x0+i*880, start=y+56, h=Math.min(42,Math.floor(660/Math.max(1,rows.length)));
      rect(ctx,x,y,w,727,'#ffffff',colors.line,18);
      rect(ctx,x+12,y+12,w-24,40,colors.navy,null,8);
      const xs=[x+24,x+525,x+675,x+w-24], widths=[350,133,133,126];
      ['Indicador',data.sides[0].name,data.sides[1].name,'Variação'].forEach((v,j)=>
        label(ctx,v,xs[j],y+32,widths[j],20,'#fff',700,j?'right':'left',12));
      rows.forEach((row,j)=>{
        const yy=start+j*h;
        if(row.group) {
          rect(ctx,x+12,yy+2,w-24,h-4,'#e9edf5',null,5);
          label(ctx,row.cells[0],xs[0],yy+h/2,w-48,21,colors.navy,700);
        } else {
          if(row.highlight || j%2===0) rect(ctx,x+12,yy,w-24,h,row.highlight?'#eef3fa':'#f8f9fb',null,4);
          row.cells.slice(0,4).forEach((v,k)=>label(ctx,v,xs[k],yy+h/2,widths[k],19,
            k===3?row.color:k===1?colors.blue:k===2?colors.orange:colors.ink,
            k||row.highlight?700:400,k?'right':'left',11));
        }
      });
      if(i===0 && start+rows.length*h+125<y+727){
        const yy=start+rows.length*h+14;
        label(ctx,'Campanhas selecionadas',x+24,yy+11,w-48,20,colors.navy,700);
        data.sides.forEach((side,j)=>{
          label(ctx,side.name,x+24,yy+40+j*42,120,18,side.color,700);
          label(ctx,side.campaign,x+150,yy+40+j*42,w-175,17,colors.ink,400,'left',11);
        });
      }
    });
    label(ctx,'Deltas calculados com valores não arredondados. Médias ignoram dias zerados.',95,985,1705,18,colors.muted);
    label(ctx,'CPC Líquido = CPC − VoiceMail. Conversão = Acordos ÷ CPC Líquido.',95,1011,1705,18,colors.muted);
  }
  function drawCombined(ctx,data) {
    const y=233, w=525;
    data.sides.forEach((s,i)=>{
      const x=95+i*540;
      rect(ctx,x,y,w,727,'#ffffff',colors.line,14);
      label(ctx,'Funil '+s.name,x+15,y+22,w-30,26,s.color,700);
      label(ctx,s.period+' · '+s.days,x+15,y+47,w-30,17,colors.muted);
      label(ctx,s.campaign,x+15,y+72,w-30,17,colors.ink,700,'left',11);
      label(ctx,'Agentes (média dia): '+s.agents,x+15,y+96,w-30,17,colors.muted);
      label(ctx,s.deltaTitle,x+w-15,y+120,150,14,colors.muted,700,'right',10);
      s.stages.forEach((stage,j)=>{
        const yy=y+131+j*42, ww=355*stage.width/100, xx=x+15+(355-ww)/2;
        ctx.beginPath();ctx.moveTo(xx,yy);ctx.lineTo(xx+ww,yy);ctx.lineTo(xx+ww-9,yy+37);ctx.lineTo(xx+9,yy+37);ctx.closePath();
        ctx.fillStyle=s.color;ctx.fill();
        label(ctx,stage.label,xx+15,yy+18,ww*.51-15,15,'#fff',700,'left',10);
        label(ctx,stage.value,xx+ww-15,yy+18,ww*.46-15,19,'#fff',700,'right',11);
        rect(ctx,x+w-133,yy+2,118,33,'#f4f6fa',colors.line,6);
        label(ctx,stage.delta,x+w-74,yy+18,108,17,stage.deltaColor,700,'center',10);
      });
      const compact=(items,yy,title)=>{
        label(ctx,title,x+15,yy+9,w-30,18,colors.navy,700);
        const cw=(w-37)/2;
        items.forEach((item,j)=>{
          const xx=x+15+(j%2)*(cw+7), rowY=yy+21+Math.floor(j/2)*31;
          rect(ctx,xx,rowY,cw,27,'#f4f6fa',colors.line,5);
          label(ctx,item.label,xx+6,rowY+13,cw-68,12,colors.muted,400,'left',9);
          label(ctx,item.value,xx+cw-6,rowY+13,57,14,colors.ink,700,'right',9);
        });
        return yy+21+Math.ceil(items.length/2)*31;
      };
      const end=compact(s.rates,y+432,'Taxas e eficiência');
      compact(s.productivity,end+2,'Produtividade por agente');
    });
    const x=1175, tw=650;
    rect(ctx,x,y,tw,727,'#fff',colors.line,14);
    rect(ctx,x+8,y+8,tw-16,35,colors.navy,null,6);
    const xs=[x+15,x+385,x+507,x+tw-15], widths=[254,107,107,105];
    ['Indicador',data.sides[0].name,data.sides[1].name,'Variação'].forEach((v,j)=>
      label(ctx,v,xs[j],y+25,widths[j],16,'#fff',700,j?'right':'left',10));
    const h=Math.min(25,Math.floor(672/data.rows.length));
    data.rows.forEach((row,j)=>{
      const yy=y+46+j*h;
      if(row.group){
        rect(ctx,x+8,yy+1,tw-16,h-2,'#e9edf5',null,4);
        label(ctx,row.cells[0],xs[0],yy+h/2,tw-30,15,colors.navy,700);
      }else{
        if(row.highlight||j%2===0) rect(ctx,x+8,yy,tw-16,h,row.highlight?'#eef3fa':'#f8f9fb',null,3);
        row.cells.slice(0,4).forEach((v,k)=>label(ctx,v,xs[k],yy+h/2,widths[k],15,
          k===3?row.color:k===1?colors.blue:k===2?colors.orange:colors.ink,
          k||row.highlight?700:400,k?'right':'left',9));
      }
    });
    label(ctx,'Mailing: média diária sem zeros. VoiceMail integra o CPC e não deve ser somado novamente. CPC Líquido = CPC − VoiceMail.',95,985,1705,18,colors.muted);
    label(ctx,'Conversão = Acordos ÷ CPC Líquido. Deltas usam valores não arredondados. Médias ignoram dias zerados.',95,1011,1705,18,colors.muted);
  }
  async function exportPNG(kind) {
    const data=snapshot();
    const bg=new Image(); bg.src=bgUrl; await bg.decode();
    const canvas=document.createElement('canvas'); canvas.width=1920;canvas.height=1080;
    const ctx=canvas.getContext('2d'); if(!ctx) throw Error('Canvas indisponível neste navegador.');
    ctx.drawImage(bg,0,0,1920,1080);
    const title=kind==='funis'?'Funis de performance e comparação':kind==='completo'?'Funis de performance e indicadores':'Visão comparativa dos indicadores';
    label(ctx,'ENERGISA  /  PERFORMANCE OPERACIONAL',95,126,1640,19,colors.orange,700);
    label(ctx,title,95,169,1705,43,colors.navy,700);
    label(ctx,data.sides.map(s=>s.name+' · '+s.period).join('    |    ')+'    |    '+data.mode+'    |    '+data.comparison,
      95,210,1705,21,colors.muted,400,'left',14);
    if(kind==='funis') drawFunnels(ctx,data); else if(kind==='completo') drawCombined(ctx,data); else drawTable(ctx,data);
    const blob=await new Promise((resolve,reject)=>canvas.toBlob(b=>b?resolve(b):reject(Error('Falha ao gerar PNG.')),'image/png'));
    const url=URL.createObjectURL(blob), a=document.createElement('a');
    a.href=url; a.download='Energisa_'+kind+'_'+new Date().toISOString().slice(0,10)+'.png';
    document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),30000);
  }
  document.querySelectorAll('[data-energisa-slide]').forEach(btn=>{
    btn.addEventListener('click',async ()=>{
      const original=btn.textContent;btn.disabled=true;btn.textContent='Gerando PNG…';
      try {await exportPNG(btn.dataset.energisaSlide);}
      catch(err) {console.error('Energisa export PNG',err);window.alert('Não foi possível exportar a imagem: '+err.message);}
      finally {btn.disabled=false;btn.textContent=original;}
    });
  });
})();