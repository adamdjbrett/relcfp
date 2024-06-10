wget -O feed.xml 'https://input.relcfp.com/feed.xml'
sed -i 's/<!\[CDATA\[//g' feed.xml
sed -i 's/]]>//g' feed.xml
sed -i 's/<br>/<br\/>/g' feed.xml
sed -i 's/<hr>/<hr\/>/g' feed.xml