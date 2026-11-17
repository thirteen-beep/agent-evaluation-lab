const {execFile} = require('node:child_process');
const path = require('node:path');
module.exports = class SupportProvider {
  constructor(options) { this.config = options.config || {}; }
  id() { return 'portfolio-support-' + (this.config.mode || 'scripted'); }
  async callApi(prompt, context) {
    const python = process.env.SUPPORT_PYTHON || 'python';
    const input = JSON.stringify({question:prompt, case:context.vars.case_id, mode:this.config.mode || 'scripted'});
    return new Promise(resolve => {
      execFile(python,[path.join(__dirname,'runner.py'),input],{timeout:360000,maxBuffer:2000000,env:{...process.env,PYTHONIOENCODING:'utf-8',PYDANTIC_AI_NO_BANNER:'1'}},(error,stdout,stderr)=>{
        if(error) return resolve({error:'Local agent process failed: '+error.message});
        try { const value=JSON.parse(stdout); resolve({output:JSON.stringify(value)}); }
        catch(e) {resolve({error:'Invalid JSON from local runner: '+e.message});}
      });
    });
  }
};
