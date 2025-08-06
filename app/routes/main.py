from flask import Blueprint, request, jsonify
from app.config import Config
from youtube_transcript_api import YouTubeTranscriptApi
from app.helpers import flatten_transcript, chunk_transcript, generate_embeddings
from app.db.setup_db import get_connection


ytt_api = YouTubeTranscriptApi()
main = Blueprint('main', __name__)

sample_transcript = [{'text': "Hey everybody, it's Doctor Jo. I got an email\nlast week from Sandra, or San-dra, sorry I", 'start': 12.8, 'duration': 6.2}, {'text': "don't know which one it actually is, but she's\na runner and she has problems with shin splints.", 'start': 19.01, 'duration': 4.38}, {'text': 'So she asked if I had any suggestions for\nsome shin stretches, and I absolutely do.', 'start': 23.39, 'duration': 5.36}]
sample_text = "Hey everybody, it's Doctor Jo. I got an email last week from Sandra, or San-dra, sorry I don't know which one it actually is, but she's a runner and she has problems with shin splints. So she asked if I had any suggestions for some shin stretches, and I absolutely do. So let's get started. Ok, so the stretches for the shin splints would be motions that you want to stretch your feet this way. When you have shin splints, most of your pain is usually on the top, it's the muscles on the top here called your anterior tibialis muscles, so to stretch those, we're gonna do pointing type exercises. The first one as I'm doing now is you're just going to point your feet forward and get a good stretch in there.You want to hold it for a little bit, 5-10 seconds. Relax. If your super flexible, once you stretch it this way, you can lean forward and push it down a little bit more. Some people aren't going to be able to do that, and that might actually be too painful to start off with, but just pointing your toes forward. If that feels easy, and it's not getting a good stretch in there, then you can roll over to use the floor to give you some extra stretch. So you can just kind of go up on your toes. See how my toes are flat, but I'm off on the ground, so I'm getting pressure through my feet. And if that seems easy as well, then you can come back and actually sit on your feet. Your toenails actually want to be on the floor. That's where you want to go. Your toes want to be flat down on the floor. And this one's gonna be a big stretch. It might hurt a little bit, but you definitely wanna push through it. You don't want it to be super painful, but you want to feel that tension. So you're just gonna rise up a little bit. You can do this stretch if it's comfortable 3 times for 30 seconds. Nice big stretch in there. And then come back down. Now the next stretches involve a noodle or a roll, kind of like when we were stretching out our IT Band in the IT Band stretches. So what this does, is this will just stretch out the muscles, loosen it up a little bit for you. You can start it at the top of the knee, and this is gonna go all the way down that anterior tibialis muscle. So you're gonna start here, and just roll forward. Nice and slow. If that feels pretty good--good kind of hurt. You can push down, get a little more pressure on there. And roll it out. Nice and slow so you're getting all those muscle fibers. You can turn your foot in a little bit, get that outer portion of the muscle. Rolling back and forth. You can do this up to a minute. Whatever's comfortable until your really start feeling those muscles loosen up a little bit. And then the last one, you want to actually stretch out your calf muscles, too, because if those are tight, that's gonna affect everything in the leg. So then you can put it right down where your Achilles Tendon is, lift your body up a little bit, and roll all the way down, and come all the way back. Same kind of thing, if that feels good, not a super stretch, push down a little harder. Give yourself a little more stretch in that calf muscle right there. Just rolling back and forth. This is great to do before you go running just to stretch out all those muscles, loosen them up so they don't get extra stress on them when you're running. Those are stretches if you have shin splints. Now if you try these stretches and it doesn't really feel like it's easing up, make sure you go to your doctor or physical therapist because it could be a body mechanics thing. You could be running wrong, or you may have shoes that are making your feet sore and causing shin splints. So make sure if this isn't helping, go to a professional and see if they can get you some help. And if it feels good, and it starts feeling better, and you want to actually strengthen your shins and your ankles muscles, then go to AskDoctorJo.com and check out some of the strengthening exercises. Alright, there you have it, so have fun, be safe, and I hope you feel better soon. I need to go to the store later to get some groceries, so I will do that after this."

split_trans = ["Hey everybody, it's Doctor Jo. I got an email last week from Sandra, or San-dra, sorry I don't know which one it actually is, but she's a runner and she has problems with shin splints. So she asked if I had any suggestions for some shin stretches, and I absolutely do.", "So let's get started. Ok, so the stretches for the shin splints would be motions that you want to stretch your feet this way. When you have shin splints, most of your pain is usually on the top, it's the muscles on the top here called your anterior tibialis muscles, so to stretch those, we're gonna do pointing type exercises. The first one as I'm doing now is you're just going to point your feet forward and get a good stretch in there.You want to hold it for a little bit, 5-10 seconds.", "Relax. If your super flexible, once you stretch it this way, you can lean forward and push it down a little bit more. Some people aren't going to be able to do that, and that might actually be too painful to start off with, but just pointing your toes forward. If that feels easy, and it's not getting a good stretch in there, then you can roll over to use the floor to give you some extra stretch. So you can just kind of go up on your toes.", "See how my toes are flat, but I'm off on the ground, so I'm getting pressure through my feet. And if that seems easy as well, then you can come back and actually sit on your feet. Your toenails actually want to be on the floor. That's where you want to go.", "Your toes want to be flat down on the floor. And this one's gonna be a big stretch. It might hurt a little bit, but you definitely wanna push through it. You don't want it to be super painful, but you want to feel that tension.", "So you're just gonna rise up a little bit. You can do this stretch if it's comfortable 3 times for 30 seconds. Nice big stretch in there. And then come back down. Now the next stretches involve a noodle or a roll, kind of like when we were stretching out our IT Band in the IT Band stretches. So what this does, is this will just stretch out the muscles, loosen it up a little bit for you. You can start it at the top of the knee, and this is gonna go all the way down that anterior tibialis muscle. So you're gonna start here, and just roll forward.", "Nice and slow. If that feels pretty good--good kind of hurt. You can push down, get a little more pressure on there. And roll it out. Nice and slow so you're getting all those muscle fibers. You can turn your foot in a little bit, get that outer portion of the muscle.", "Rolling back and forth. You can do this up to a minute. Whatever's comfortable until your really start feeling those muscles loosen up a little bit. And then the last one, you want to actually stretch out your calf muscles, too, because if those are tight, that's gonna affect everything in the leg. So then you can put it right down where your Achilles Tendon is, lift your body up a little bit, and roll all the way down, and come all the way back. Same kind of thing, if that feels good, not a super stretch, push down a little harder.", "Give yourself a little more stretch in that calf muscle right there. Just rolling back and forth. This is great to do before you go running just to stretch out all those muscles, loosen them up so they don't get extra stress on them when you're running. Those are stretches if you have shin splints. Now if you try these stretches and it doesn't really feel like it's easing up, make sure you go to your doctor or physical therapist because it could be a body mechanics thing. You could be running wrong, or you may have shoes that are making your feet sore and causing shin splints. So make sure if this isn't helping, go to a professional and see if they can get you some help. And if it feels good, and it starts feeling better, and you want to actually strengthen your shins and your ankles muscles, then go to AskDoctorJo.com and check out some of the strengthening exercises. Alright, there you have it, so have fun, be safe, and I hope you feel better soon.", 'I need to go to the store later to get some groceries, so I will do that after this.']

@main.route("/haste", methods=["POST"])
def haste():
    data = request.get_json()
    if not data or "video_id" not in data:
        return jsonify({"error": "No video id provided"}), 400
    
    video_id = data["video_id"]
    print(data)
    return jsonify({"message": "Hello, world!"})

@main.route("/embed_transcript", methods=["POST"])
def embed_transcript():
    data = request.get_json()
    if not data or "video_id" not in data:
        return jsonify({"error": "No video id provided"}), 400
    
    video_id = data["video_id"]

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM videos WHERE video_id = %s", (video_id,))
                if cursor.fetchone():
                    return jsonify({"message": "Video already exists."}), 200
                
                transcript = ytt_api.fetch(video_id).to_raw_data()

                if not transcript:
                    return jsonify({"error": "No transcript found for the provided video id"}), 404
                
                cursor.execute(
                    "INSERT INTO videos (video_id, title, description) VALUES (%s, %s, %s) RETURNING id",
                    (video_id, data["title"], data.get("description", ""))
                )
                video_db_id = cursor.fetchone()[0]
    
                flat_transcript = flatten_transcript(transcript)
                chunked_transcript = chunk_transcript(flat_transcript)

                generate_embeddings(chunked_transcript, video_db_id, cursor)
                conn.commit()

        return jsonify({"message": "Embeddings generated successfully!"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
