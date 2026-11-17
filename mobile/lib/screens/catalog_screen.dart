import 'package:flutter/material.dart';
import '../models/story_models.dart';
import '../services/api_client.dart';
import 'story_screen.dart';

class CatalogScreen extends StatefulWidget {
  const CatalogScreen({super.key});
  @override
  State<CatalogScreen> createState()=>_CatalogScreenState();
}
class _CatalogScreenState extends State<CatalogScreen> {
  final AudioVerseApi _api=AudioVerseApi();
  late Future<List<StorySummary>> _works;
  @override void initState(){super.initState();_works=_api.catalog();}
  @override void dispose(){_api.dispose();super.dispose();}
  @override Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title:const Text('◉ AudioVerse'), backgroundColor: Colors.transparent),
    body:SafeArea(child:Padding(padding:const EdgeInsets.all(20),child:Column(
      crossAxisAlignment:CrossAxisAlignment.start,children:[
        Text('TRUYỆN AUDIO TƯƠNG TÁC',style:TextStyle(color:Theme.of(context).colorScheme.primary,letterSpacing:2)),
        const SizedBox(height:8),
        const Text('Một câu chuyện.\nNhiều số phận.',style:TextStyle(fontSize:33,fontWeight:FontWeight.w800)),
        const SizedBox(height:14),
        const Text('Bản demo chạy với backend cục bộ. Chỉ sử dụng nội dung nguyên bản.',style:TextStyle(color:Colors.white70)),
        const SizedBox(height:28),
        Expanded(child:FutureBuilder<List<StorySummary>>(
          future:_works,builder:(context,snapshot){
            if(snapshot.hasError) return Center(child:Column(mainAxisSize:MainAxisSize.min,children:[
              const Text('Không kết nối được backend local.'),const SizedBox(height:8),
              Text('${snapshot.error}',textAlign:TextAlign.center),
              TextButton(onPressed:()=>setState(()=>_works=_api.catalog()),child:const Text('Thử lại'))]));
            if(!snapshot.hasData)return const Center(child:CircularProgressIndicator());
            return ListView.builder(itemCount:snapshot.data!.length,itemBuilder:(context,index){
              final story=snapshot.data![index];
              return Card(child:Padding(padding:const EdgeInsets.all(16),child:Column(
                crossAxisAlignment:CrossAxisAlignment.start,children:[
                  const Text('AUDIOVERSE ORIGINAL',style:TextStyle(fontSize:11,letterSpacing:2)),
                  const SizedBox(height:12),Text(story.title,style:const TextStyle(fontSize:24,fontWeight:FontWeight.bold)),
                  const SizedBox(height:8),Text(story.description),const SizedBox(height:12),
                  Text(story.genre,style:const TextStyle(color:Colors.white60)),
                  const SizedBox(height:8),FilledButton.icon(icon:const Icon(Icons.headphones),
                    label:const Text('Bắt đầu trải nghiệm'),onPressed:()=>Navigator.push(context,
                      MaterialPageRoute(builder:(_)=>StoryScreen(story:story))),),
                ])));
            });
          },
        )),
      ]))),
  );
}
