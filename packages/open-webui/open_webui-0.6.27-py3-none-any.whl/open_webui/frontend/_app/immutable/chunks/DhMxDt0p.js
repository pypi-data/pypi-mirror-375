import{p as K}from"./BJaBlHh6.js";import{Y as S,P as F,aI as Y,E as Z,o as q,p as H,s as J,g as Q,c as X,b as ee,_ as g,l as z,v as te,d as ae,F as re,K as ne,a6 as ie,k as se}from"./ClMPswyK.js";import{p as le}from"./C-dj-c58.js";import{d as R}from"./Ch9pnHr_.js";import{o as oe}from"./CmKTTxBW.js";function ce(e,a){return a<e?-1:a>e?1:a>=e?0:NaN}function ue(e){return e}function pe(){var e=ue,a=ce,f=null,x=S(0),s=S(F),o=S(0);function l(t){var n,c=(t=Y(t)).length,u,y,m=0,p=new Array(c),i=new Array(c),v=+x.apply(this,arguments),w=Math.min(F,Math.max(-F,s.apply(this,arguments)-v)),h,C=Math.min(Math.abs(w)/c,o.apply(this,arguments)),$=C*(w<0?-1:1),d;for(n=0;n<c;++n)(d=i[p[n]=n]=+e(t[n],n,t))>0&&(m+=d);for(a!=null?p.sort(function(A,D){return a(i[A],i[D])}):f!=null&&p.sort(function(A,D){return f(t[A],t[D])}),n=0,y=m?(w-c*$)/m:0;n<c;++n,v=h)u=p[n],d=i[u],h=v+(d>0?d*y:0)+$,i[u]={data:t[u],index:n,value:d,startAngle:v,endAngle:h,padAngle:C};return i}return l.value=function(t){return arguments.length?(e=typeof t=="function"?t:S(+t),l):e},l.sortValues=function(t){return arguments.length?(a=t,f=null,l):a},l.sort=function(t){return arguments.length?(f=t,a=null,l):f},l.startAngle=function(t){return arguments.length?(x=typeof t=="function"?t:S(+t),l):x},l.endAngle=function(t){return arguments.length?(s=typeof t=="function"?t:S(+t),l):s},l.padAngle=function(t){return arguments.length?(o=typeof t=="function"?t:S(+t),l):o},l}var L=Z.pie,G={sections:new Map,showData:!1,config:L},T=G.sections,N=G.showData,ge=structuredClone(L),de=g(()=>structuredClone(ge),"getConfig"),fe=g(()=>{T=new Map,N=G.showData,te()},"clear"),he=g(({label:e,value:a})=>{if(a<0)throw new Error(`"${e}" has invalid value: ${a}. Negative values are not allowed in pie charts. All slice values must be >= 0.`);T.has(e)||(T.set(e,a),z.debug(`added new section: ${e}, with value: ${a}`))},"addSection"),me=g(()=>T,"getSections"),ve=g(e=>{N=e},"setShowData"),Se=g(()=>N,"getShowData"),_={getConfig:de,clear:fe,setDiagramTitle:q,getDiagramTitle:H,setAccTitle:J,getAccTitle:Q,setAccDescription:X,getAccDescription:ee,addSection:he,getSections:me,setShowData:ve,getShowData:Se},xe=g((e,a)=>{K(e,a),a.setShowData(e.showData),e.sections.map(a.addSection)},"populateDb"),ye={parse:g(async e=>{const a=await le("pie",e);z.debug(a),xe(a,_)},"parse")},we=g(e=>`
  .pieCircle{
    stroke: ${e.pieStrokeColor};
    stroke-width : ${e.pieStrokeWidth};
    opacity : ${e.pieOpacity};
  }
  .pieOuterCircle{
    stroke: ${e.pieOuterStrokeColor};
    stroke-width: ${e.pieOuterStrokeWidth};
    fill: none;
  }
  .pieTitleText {
    text-anchor: middle;
    font-size: ${e.pieTitleTextSize};
    fill: ${e.pieTitleTextColor};
    font-family: ${e.fontFamily};
  }
  .slice {
    font-family: ${e.fontFamily};
    fill: ${e.pieSectionTextColor};
    font-size:${e.pieSectionTextSize};
    // fill: white;
  }
  .legend text {
    fill: ${e.pieLegendTextColor};
    font-family: ${e.fontFamily};
    font-size: ${e.pieLegendTextSize};
  }
`,"getStyles"),Ae=we,De=g(e=>{const a=[...e.values()].reduce((s,o)=>s+o,0),f=[...e.entries()].map(([s,o])=>({label:s,value:o})).filter(s=>s.value/a*100>=1).sort((s,o)=>o.value-s.value);return pe().value(s=>s.value)(f)},"createPieArcs"),Ce=g((e,a,f,x)=>{z.debug(`rendering pie chart
`+e);const s=x.db,o=ae(),l=re(s.getConfig(),o.pie),t=40,n=18,c=4,u=450,y=u,m=ne(a),p=m.append("g");p.attr("transform","translate("+y/2+","+u/2+")");const{themeVariables:i}=o;let[v]=ie(i.pieOuterStrokeWidth);v??(v=2);const w=l.textPosition,h=Math.min(y,u)/2-t,C=R().innerRadius(0).outerRadius(h),$=R().innerRadius(h*w).outerRadius(h*w);p.append("circle").attr("cx",0).attr("cy",0).attr("r",h+v/2).attr("class","pieOuterCircle");const d=s.getSections(),A=De(d),D=[i.pie1,i.pie2,i.pie3,i.pie4,i.pie5,i.pie6,i.pie7,i.pie8,i.pie9,i.pie10,i.pie11,i.pie12];let E=0;d.forEach(r=>{E+=r});const P=A.filter(r=>(r.data.value/E*100).toFixed(0)!=="0"),b=oe(D);p.selectAll("mySlices").data(P).enter().append("path").attr("d",C).attr("fill",r=>b(r.data.label)).attr("class","pieCircle"),p.selectAll("mySlices").data(P).enter().append("text").text(r=>(r.data.value/E*100).toFixed(0)+"%").attr("transform",r=>"translate("+$.centroid(r)+")").style("text-anchor","middle").attr("class","slice"),p.append("text").text(s.getDiagramTitle()).attr("x",0).attr("y",-(u-50)/2).attr("class","pieTitleText");const W=[...d.entries()].map(([r,M])=>({label:r,value:M})),k=p.selectAll(".legend").data(W).enter().append("g").attr("class","legend").attr("transform",(r,M)=>{const O=n+c,V=O*W.length/2,U=12*n,j=M*O-V;return"translate("+U+","+j+")"});k.append("rect").attr("width",n).attr("height",n).style("fill",r=>b(r.label)).style("stroke",r=>b(r.label)),k.append("text").attr("x",n+c).attr("y",n-c).text(r=>s.getShowData()?`${r.label} [${r.value}]`:r.label);const B=Math.max(...k.selectAll("text").nodes().map(r=>(r==null?void 0:r.getBoundingClientRect().width)??0)),I=y+t+n+c+B;m.attr("viewBox",`0 0 ${I} ${u}`),se(m,u,I,l.useMaxWidth)},"draw"),$e={draw:Ce},Fe={parser:ye,db:_,renderer:$e,styles:Ae};export{Fe as diagram};
//# sourceMappingURL=DhMxDt0p.js.map
