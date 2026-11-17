import 'dart:math';
import 'package:flutter/material.dart';
import 'package:just_audio/just_audio.dart';
import '../models/story_models.dart';
import '../services/api_client.dart';

class StoryScreen extends StatefulWidget {
  const StoryScreen({required this.story,super.key});
  final StorySummary story;
  @override State<StoryScreen> createState()=>_StoryScreenState();
}
class _StoryScreenState extends State<StoryScreen> {
  final AudioVerseApi _api=AudioVerseApi();
  final AudioPlayer _player=AudioPlayer();
  StoryRun? _run;
  String? _error;
  bool _busy=true;
  @override void initState(){super.initState();_begin();}
  @override void dispose(){_player.dispose();_api.dispose();super.dispose();}
  Future<void> _begin() async {
    setState((){_busy=true;_error=null;});
    try {final run=await _api.begin(widget.story.id);await _load(run);}
    catch(e){if(mounted)setState((){_error='$e';_busy=false;});}
  }
  Future<void> _load(StoryRun run) async {
    await _player.stop();
    await _player.setUrl(_api.sceneAudioUrl(run.scene.id));
    if(mounted)setState((){_run=run;_busy=false;_error=null;});
  }
  String _newKey(){final r=Random.secure();return List.generate(24,(_)=>r.nextInt(16).toRadixString(16)).join();}
  Future<void> _choose(StoryChoice choice) async {
    if(_busy || _run==null)return;
    setState(()=>_busy=true);
    try {final newRun=await _api.choose(_run!,choice.id,_newKey());await _load(newRun);}
    catch(e){if(mounted)setState((){_error='$e';_busy=false;});}
  }
  @override Widget build(BuildContext context) {
    final run=_run;
    return Scaffold(appBar:AppBar(title:Text(widget.story.title),backgroundColor:Colors.transparent),
      body:SafeArea(child:ListView(padding:const EdgeInsets.all(20),children:[
        const Text('BẢN CHẠY DEMO · GIỌNG TỔNG HỢP',style:TextStyle(fontSize:11,color:Colors.white60,letterSpacing:1)),
        if(_error!=null) Padding(padding:const EdgeInsets.symmetric(vertical:12),child:Text(_error!,style:const TextStyle(color:Colors.orangeAccent))),
        if(run==null) Center(child:_busy?const CircularProgressIndicator():FilledButton(onPressed:_begin,child:const Text('Thử lại'))),
        if(run!=null) ...[
          const SizedBox(height:18),Text(run.scene.title,style:const TextStyle(fontSize:27,fontWeight:FontWeight.bold)),
          const SizedBox(height:14),Text(run.scene.text,style:const TextStyle(fontSize:17,height:1.7)),
          for(final note in run.scene.memoryNotes) Padding(padding:const EdgeInsets.only(top:10),child:Text('◆ $note',style:const TextStyle(color:Color(0xFFE5BC7B)))),
          const SizedBox(height:24),
          Card(child:Padding(padding:const EdgeInsets.all(15),child:Column(children:[
            const Text('Giọng đọc demo · eSpeak'),
            const SizedBox(height:5),StreamBuilder<bool>(stream:_player.playingStream,builder:(context,snapshot)=>
              IconButton.filledTonal(iconSize:30,onPressed:_busy?null:()=>snapshot.data==true?_player.pause():_player.play(),
                icon:Icon(snapshot.data==true?Icons.pause:Icons.play_arrow))),
            StreamBuilder<Duration>(stream:_player.positionStream,builder:(context,snapshot){
              final duration=_player.duration ?? Duration.zero;
              final max=duration.inMilliseconds.toDouble();
              final value=(snapshot.data ?? Duration.zero).inMilliseconds.toDouble().clamp(0.0,max).toDouble();
              return Slider(value:value,max:max>0?max:1,onChanged:max>0?(v)=>_player.seek(Duration(milliseconds:v.toInt())):null);
            }),
          ]))),
          const SizedBox(height:14),if(!run.scene.ending) const Text('Bạn muốn làm gì?',style:TextStyle(fontWeight:FontWeight.bold,fontSize:18)),
          const SizedBox(height:8),for(final choice in run.scene.choices) Padding(
            padding:const EdgeInsets.only(bottom:8),child:OutlinedButton(
              onPressed:_busy?null:()=>_choose(choice),child:Padding(padding:const EdgeInsets.all(10),child:Text(choice.label))),
          ),
          if(run.scene.ending) ...[const Text('Bạn đã đến một kết cục.',style:TextStyle(fontWeight:FontWeight.bold)),
            const SizedBox(height:10),FilledButton(onPressed:_busy?null:_begin,child:const Text('Chơi lại từ đầu'))],
          if(_busy)const LinearProgressIndicator(),
        ],
      ])),
    );
  }
}
