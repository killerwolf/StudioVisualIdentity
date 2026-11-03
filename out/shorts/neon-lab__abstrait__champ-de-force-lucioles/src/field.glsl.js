// field.glsl.js — « champ de force » de fond, signature Labo Néon (partagé tel quel par les 2 shorts).
// Fonction GLSL pure : lignes iso d'un potentiel (bruit fbm + puits radial), boucle parfaite via uLoop=(cos,sin)(2πt/T).
// Hôtes : twgl.js (short abstrait, WebGL2 #version 300 es) et three.js ShaderMaterial (short explicatif).
export const FIELD_GLSL = /* glsl */`
float nl_h(vec2 p){ p=fract(p*vec2(123.34,456.21)); p+=dot(p,p+45.32); return fract(p.x*p.y); }
float nl_vn(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.-2.*f);
  return mix(mix(nl_h(i),nl_h(i+vec2(1.,0.)),f.x), mix(nl_h(i+vec2(0.,1.)),nl_h(i+vec2(1.,1.)),f.x), f.y); }
float nl_fbm(vec2 p){ return .6*nl_vn(p)+.3*nl_vn(p*2.03+7.1)+.1*nl_vn(p*4.01+3.3); }
// fc : gl_FragCoord.xy ; res : (W,H) ; center : puits du champ en px ; loop : (cos,sin) de la phase ; pulse : 0..1
vec3 neonField(vec2 fc, vec2 res, vec2 center, vec2 loop, float pulse, float strength){
  vec2 p=(fc-center)/res.y;
  float r=length(p);
  vec2 q=p*3.0+loop*0.32;
  float f=nl_fbm(q)*0.9+0.42/(r*5.5+1.0);
  float k=f*11.0;
  float w=fwidth(k);
  float dl=0.5-abs(fract(k)-0.5);            // distance à la ligne iso la plus proche
  float iso=1.0-smoothstep(0.0, w*1.6, dl);
  float side=smoothstep(0.25,0.75,nl_fbm(p*1.4-loop*0.2+5.0));
  vec3 cyan=vec3(0.2196,0.9765,1.0), mag=vec3(1.0,0.2392,0.796);
  vec3 lineCol=mix(cyan,mag,side);
  vec3 bg=vec3(0.0196,0.0235,0.0431);
  vec3 surf=vec3(0.0667,0.0784,0.1647);
  float glow=exp(-r*r*5.0);
  float vign=smoothstep(1.05,0.25,r);
  vec3 c=mix(bg,surf,glow*0.85);
  c+=lineCol*iso*(0.10+0.14*pulse)*vign*strength;
  return c;
}
`;
