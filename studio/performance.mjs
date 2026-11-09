// SPDX-License-Identifier: MIT
import {compile,sectionProject,songSections,validatePresets} from './model.mjs';
export function parameters(p){const result={morph:p.morph??0,breath:p.breath??6,vibrato:p.vibrato??20,glide:p.glide??50,harmony:p.harmony??0,expression:p.expression??110,emotion:p.emotion??0};validatePresets(Array(8).fill({name:'preview',voice:p.voice??0,style:p.style??0,...result}));return result;}
export function timeline(project,dictionary){
 if(project.events||(!project.sectionSettings&&!project.sectionModes))return [{tick:0,voice:project.voice??0,style:project.style??0,parameters:parameters(project)}];
 let tick=0;return songSections(project.lyrics).map((_,i)=>{const p=sectionProject(project,i),entry={tick,voice:p.voice??0,style:p.style??0,parameters:parameters(p)};tick+=compile(p,dictionary).ticks;return entry;});
}
export function applyProfile(engine,profile){engine.web_voice(profile.voice,profile.style);const p=profile.parameters;engine.web_parameters(p.morph,p.breath,p.vibrato,p.glide,p.harmony,p.expression,p.emotion);}
export class ProfileTimeline{
 constructor(engine,profiles){this.engine=engine;this.profiles=profiles;this.index=0;if(profiles.length)applyProfile(engine,profiles[0]);}
 advance(tick){while(this.index+1<this.profiles.length&&tick>=this.profiles[this.index+1].tick)applyProfile(this.engine,this.profiles[++this.index]);return this.profiles[this.index]?.parameters.emotion??0;}
}
