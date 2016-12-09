# TalkBots #

Stream an audio conversation of two chatterbots talking to one another.

## Acquire Image ##
You can either build from this repo:
```bash
docker build . --tag gaboose/talkbots
```

Or pull from docker hub:
```bash
docker pull gaboose/talkbots # (1.164 GB)
```

## Run ##

```bash
# This streams RTP audio to 172.17.0.1 - default host machine address (this may be different for a Windows host)
docker run -it --rm gaboose/talkbots
# If you wish to stream to another IP, run:
docker run -it --rm -e STREAM_TARGET=<ipaddress> gaboose/talkbots
```

Then open the `rtp://@:5555` url on VLC.

# Instrukcijos Mikalojui #

Aš sugalvojau šitą programėlę supakuot į tokį vadinamą Docker konteinerį, kad būtų lengviau ir patikimiau suinstaliuot/perkelt ją iš vieno kompo į kitą. Turėtų veikt ir ant Windowsų ir ant Linuxų. The catch is, kad tau teks susiintaliuot patį Dockerį pirmiausia. 

[Setting Up Docker on Windows](https://www.youtube.com/watch?v=S7NVloq0EBc) <- šitas turėtų pagelbėt.

[Install Docker on Ubuntu](https://docs.docker.com/engine/installation/linux/ubuntulinux/) <- o čia jei nori paleist ant linuxų. Biški sunkiau suinstaliuot. Gal reiktų pasilikt kaip atsarginį variantą, jei su Windowsais neišeis.

Suinstaliavus tam command-line tada tereiks paleist šitas dvi komandas:

```bash
docker pull gaboose/talkbots
...
docker run -it --rm -e STREAM_TARGET=<ipaddress> gaboose/talkbots
```

Visai kaip aukščiau angliškose instrukcijose parašiau. Tik vietoj `<ipaddress>` reiks įrašyt laptopo IP adresą. Jį kažkaip reikia atrasti per Windowsus. Dar nežinau tiksliai kaip, galėsim kartu padaryt. Kompai dažnai turi kelis IP adresus (vienas adresas per interfeisą) ir čia idealiai reikėtų įrašyt to pačio interfeiso, prie kurio yra prijungtas docker virtual machine (private network, kaip ten sako filmuke), bet gal veiks ir bet kuris (ant linuxų veikė).

Ir tada atsidarai `rtp://@:5555` per VLC ir turėtum išgirst juos besikalbant :)