"""KK symbol guide for the word pages (tools/build_word_pages.py): how to make each sound, in Chinese
for the page and English for the owner's gloss. One line per symbol, used in each page's
「用到的音」 table, which links the symbol to the full KK chart."""

SOUNDS = {
    "i":  ("長母音：嘴角往兩邊拉開、舌頭在前面高處，像微笑。", "Long vowel: spread the lips, tongue high and front, like a smile."),
    "ɪ":  ("短而放鬆的母音：比 [i] 短，嘴角不要用力拉開。", "Short, relaxed vowel: shorter than [i], don't pull the lips wide."),
    "e":  ("嘴巴從半開滑向 [ɪ]，是兩段的音，如 day、cake。", "The mouth glides from half-open toward [ɪ] — two parts, as in day, cake."),
    "ɛ":  ("嘴巴半開、嘴角稍微拉開，比 [æ] 小，如 bed。", "Mouth half open, lips slightly spread, smaller than [æ], as in bed."),
    "æ":  ("嘴巴張大、下巴往下、嘴角往兩邊拉，如 cat；不要唸成 [ɛ]。", "Mouth wide open, jaw down, lips spread, as in cat; don't say [ɛ]."),
    "ɑ":  ("嘴巴張大、舌頭放低往後，如 hot、doctor。", "Mouth wide open, tongue low and back, as in hot, doctor."),
    "ɔ":  ("嘴唇微圓、開口比 [o] 大，如 walk、talk。", "Lips slightly rounded, wider open than [o], as in walk, talk."),
    "o":  ("嘴唇圓、從 [o] 滑向 [ʊ]，如 go、photo。", "Rounded lips gliding from [o] toward [ʊ], as in go, photo."),
    "ʊ":  ("短而放鬆的圓唇音，如 book、good。", "Short, relaxed rounded vowel, as in book, good."),
    "u":  ("長的圓唇音，嘴唇往前噘，如 food、moon。", "Long rounded vowel, lips pushed forward, as in food, moon."),
    "ʌ":  ("嘴巴半開、放鬆，短而清楚，出現在重音節，如 cup、mother。", "Mouth half open and relaxed, short and clear, in stressed syllables, as in cup, mother."),
    "ə":  ("最輕、最短的弱母音，只出現在不重音的音節，輕輕帶過。", "The lightest, shortest weak vowel; only in unstressed syllables — just pass through it."),
    "ɝ":  ("重音節的捲舌母音：舌尖往後捲、不碰上顎，如 bird、girl。", "Stressed r-colored vowel: curl the tongue tip back without touching the roof of the mouth, as in bird, girl."),
    "ɚ":  ("不重音的捲舌音，輕輕捲舌帶過，如 water、teacher 的字尾。", "Unstressed r-colored vowel: a light curl, as at the end of water, teacher."),
    "aɪ": ("從 [ɑ] 滑到 [ɪ]，如 eye、five。", "Glide from [ɑ] to [ɪ], as in eye, five."),
    "aʊ": ("從 [ɑ] 滑到 [ʊ]，嘴巴由開到圓，如 mouth、now。", "Glide from [ɑ] to [ʊ], the mouth going from open to round, as in mouth, now."),
    "ɔɪ": ("從 [ɔ] 滑到 [ɪ]，如 boy、toy。", "Glide from [ɔ] to [ɪ], as in boy, toy."),
    "p":  ("雙唇閉緊再放開，送出一口氣，聲帶不震動。", "Close both lips, then release with a puff of air; no voice."),
    "b":  ("雙唇閉緊再放開，聲帶震動。", "Close both lips, then release; voiced."),
    "t":  ("舌尖頂住上排牙齦再放開送氣；美式在兩個母音中間常變得很輕，如 water。", "Tongue tip on the gum ridge, release with air; in American English it often goes soft between vowels, as in water."),
    "d":  ("舌尖頂住上排牙齦再放開，聲帶震動。", "Tongue tip on the gum ridge, release; voiced."),
    "k":  ("舌根頂住上顎後方再放開送氣。", "Back of the tongue against the back of the roof of the mouth, release with air."),
    "g":  ("舌根頂住上顎後方再放開，聲帶震動。", "Back of the tongue against the back of the roof of the mouth, release; voiced."),
    "f":  ("上排牙齒輕碰下唇吹氣，聲帶不震動。", "Upper teeth lightly on the lower lip, blow air; no voice."),
    "v":  ("上排牙齒輕碰下唇，聲帶震動；不要唸成 [w] 或 [b]。", "Upper teeth lightly on the lower lip, voiced; don't say [w] or [b]."),
    "θ":  ("舌尖輕放在上下門牙之間吹氣，聲帶不震動；不要唸成 [s] 或 [f]。", "Tongue tip lightly between the front teeth, blow air, no voice; don't say [s] or [f]."),
    "ð":  ("舌尖放在上下門牙之間，聲帶震動；不要唸成 [d] 或 [z]。", "Tongue tip between the front teeth, voiced; don't say [d] or [z]."),
    "s":  ("舌尖靠近上排牙齦，送出細細的氣流。", "Tongue tip near the gum ridge, a thin stream of air."),
    "z":  ("跟 [s] 同位置，但聲帶震動，像蜜蜂的嗡嗡聲；在字尾也要唸出來。", "Same place as [s] but voiced, like a bee's buzz; say it at the end of words too."),
    "ʃ":  ("嘴唇微微往前噘，送出比 [s] 粗的氣流，如 she。", "Lips pushed slightly forward, a wider stream of air than [s], as in she."),
    "ʒ":  ("跟 [ʃ] 同嘴型，但聲帶震動，如 television、usually。", "Same mouth shape as [ʃ] but voiced, as in television, usually."),
    "tʃ": ("舌尖先頂住牙齦再放開成 [ʃ]，嘴唇微噘，如 chair。", "Tongue tip on the gum ridge, released into [ʃ], lips slightly forward, as in chair."),
    "dʒ": ("跟 [tʃ] 同嘴型，但聲帶震動，如 orange、juice。", "Same mouth shape as [tʃ] but voiced, as in orange, juice."),
    "h":  ("從喉嚨輕輕呼氣，不要太用力。", "A light breath from the throat, not forced."),
    "m":  ("雙唇閉合，聲音從鼻子出來。", "Lips closed, the sound comes through the nose."),
    "n":  ("舌尖頂住上排牙齦，聲音從鼻子出來；在字尾要頂住再結束。", "Tongue tip on the gum ridge, sound through the nose; at the end of a word, hold the tongue there before stopping."),
    "ŋ":  ("舌根頂住上顎後方，聲音從鼻子出來，如 sing、English。", "Back of the tongue against the back of the roof of the mouth, sound through the nose, as in sing, English."),
    "l":  ("舌尖頂住上排牙齦；在字尾的 l 舌尖也要往上頂，不要省略。", "Tongue tip on the gum ridge; at the end of a word, still lift the tongue tip — don't drop it."),
    "r":  ("舌頭往後捲、不碰上顎，嘴唇微圓；不要唸成 [l]。", "Tongue curled back without touching the roof of the mouth, lips slightly round; don't say [l]."),
    "w":  ("嘴唇先噘圓再快速放開，如 water、world。", "Round the lips, then quickly open them, as in water, world."),
    "j":  ("舌面往上顎靠近，像很短的 [i]，如 yes、music。", "Tongue body up toward the roof of the mouth, like a very short [i], as in yes, music."),
    "ḷ":  ("成音節的 l：前一個子音之後直接把舌尖往上頂唸 l，中間不加母音，如 little、apple。", "Syllabic l: right after the consonant, lift the tongue tip for l with no vowel in between, as in little, apple."),
    "ṇ":  ("成音節的 n：[t] 或 [d] 之後舌尖不離開牙齦，直接從鼻子出聲，如 button、garden。", "Syllabic n: after [t] or [d] the tongue tip stays on the gum ridge and the sound goes through the nose, as in button, garden."),
}

ORDER = sorted(SOUNDS, key=len, reverse=True)          # match tʃ before t, aɪ before a …

def split(kk):
    """KK string → the list of symbols in it (stress marks dropped)."""
    s, out = kk.replace("ˈ", "").replace("ˌ", ""), []
    i = 0
    while i < len(s):
        for sym in ORDER:
            if s.startswith(sym, i):
                out.append(sym); i += len(sym); break
        else:
            i += 1
    return out
