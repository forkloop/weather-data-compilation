require "net/http"
require "date"
require "fileutils"
require "logger"
require "openssl"
require "base64"

log = Logger.new(DateTime.now.strftime("s3-upload-%Y-%m-%d-%H-%M.log"))

weather_dirname = DateTime.now.strftime("weather-%Y-%m-%d-%H")
begin
  Dir.mkdir(weather_dirname)
rescue => sce
  log.error("#{sce.class}: #{sce.message}")
  exit(1)
end

ydate = (Date.today - 1).strftime("%Y-%m-%d")
yfiles = Dir.glob("*#{ydate}*.dat")
log.info("# of weather data files: #{yfiles.size.to_s}")
FileUtils.cp yfiles, weather_dirname

tar_output = `tar czf #{weather_dirname}.tar.gz #{weather_dirname}` 
log.info(tar_output)

# Upload to S3
AWS_ACCESS_KEY_ID = ENV["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = ENV["AWS_SECRET_ACCESS_KEY"]
BUCKET = "weather-data-compilation"
DIGEST = OpenSSL::Digest::Digest.new('sha1')
header_date = Time.now.utc.strftime('%a, %d %b %Y %T GMT')
url_to_sign = "PUT\n\n\n#{header_date}\n/#{BUCKET}/#{weather_dirname}.tar.gz"
signature = OpenSSL::HMAC.digest(DIGEST, AWS_SECRET_ACCESS_KEY, url_to_sign)
encoded_signature = Base64.encode64(signature)

uri = URI.parse("http://s3.amazonaws.com/#{BUCKET}/#{weather_dirname}.tar.gz")
req = Net::HTTP::Put.new(uri.path)
req["Date"] = header_date
req["Authorization"] = "AWS #{AWS_ACCESS_KEY_ID}:#{encoded_signature}"
req.body = File.read("#{weather_dirname}.tar.gz")
res = Net::HTTP.start(uri.host, uri.port) do |http|
  http.request(req)
end
