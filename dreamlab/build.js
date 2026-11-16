#!/usr/bin/env node
/* Ghép src/head.html + css + src/partials/*.html (theo thứ tự tên file) + js thành trang.
   node build.js        -> index.html (bản artifact, không doctype) + site.html (bản đầy đủ để host/test)
   node build.js A      -> _A.html (bản đầy đủ, để từng session test riêng, không ghi đè của nhau) */
const fs=require('fs'),path=require('path'),R=__dirname,ex=f=>fs.existsSync(path.join(R,f));
const css=['css/fonts.css','css/tokens.css','css/base.css','css/core.css','css/work.css','css/lab.css','css/samples.css'].filter(ex);
const js=['vendor/gsap.min.js','vendor/ScrollTrigger.min.js','vendor/SplitText.min.js','vendor/lenis.min.js','js/data.js','js/kit.js','js/core.js','js/work.js','js/lab.js'].filter(ex).concat(fs.readdirSync(path.join(R,'js')).filter(f=>/^samples-.+\.js$/.test(f)).sort().map(f=>'js/'+f),['js/samples.js'].filter(ex));
const pdir=path.join(R,'src/partials');
const parts=fs.readdirSync(pdir).filter(f=>f.endsWith('.html')).sort().map(f=>`<!-- ${f} -->\n`+fs.readFileSync(path.join(pdir,f),'utf8').trim());
const head=fs.readFileSync(path.join(R,'src/head.html'),'utf8').trim();
const v=Date.now().toString(36);
const frag=[head,...css.map(c=>`<link rel="stylesheet" href="${c}">`),...parts,...js.map(s=>`<script src="${s}"></script>`)].join('\n')+'\n';
const full=`<!doctype html>\n<html lang="vi">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n<style>:root{color-scheme:light;padding:env(safe-area-inset-top,0px) 0 env(safe-area-inset-bottom,0px)}[hidden]{display:none!important}</style>\n</head>\n<body>\n${frag}</body>\n</html>\n`;
const tag=process.argv[2];
if(tag){fs.writeFileSync(path.join(R,`_${tag}.html`),full);console.log(`_${tag}.html`,parts.length,'partials')}
else{fs.writeFileSync(path.join(R,'index.html'),frag);fs.writeFileSync(path.join(R,'site.html'),full);console.log('index.html + site.html',parts.length,'partials',css.length,'css',js.length,'js')}
