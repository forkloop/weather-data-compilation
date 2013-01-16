#!/usr/bin/env ruby

# Prefer single quote when you don't need string interpolation.
require 'rubygems'
require 'date'
require 'time'
require 'logger'
require 'aws-sdk'

log = Logger.new(STDOUT)
log.level = Logger::DEBUG

DATA_DIR = File.expand_path('../data', __FILE__)
log.debug(DATA_DIR)

# Enforce there is a `data` directory.
if !File.directory? DATA_DIR
  abort("#{DATA_DIR} does not exist!")
end

# Get the timestamp of latest file.
previous_data = Dir.entries(DATA_DIR)
latest_timestamp = 0
previous_data.each do |data|
  log.debug("Checking #{data}")
  match_data = /\d{4}-\d{2}-\d{2}/.match(data)
  if !!match_data
    timestamp = Time.parse(Date.parse(match_data.to_s).to_s).to_i
    if timestamp > latest_timestamp
      latest_timestamp = timestamp
    end
  else
    log.debug("Ignore file: #{data}")
  end
end
log.info("Latest file date: #{Time.at(latest_timestamp).strftime('%Y-%m-%d')}")

# Start to download.
SECONDS_PER_DAY = 24 * 3600
today_timestamp = Time.parse(Date.today.to_s).to_i
s3 = AWS::S3.new(:access_key_id => ENV['AWS_ACCESS_KEY_ID'], 
                 :secret_access_key => ENV['AWS_SECRET_ACCESS_KEY'])
BUCKET = s3.buckets['weather-data-compilation']
latest_timestamp += SECONDS_PER_DAY
while latest_timestamp < today_timestamp do
  file_to_download = "weather-data-#{Time.at(latest_timestamp).strftime('%Y-%m-%d')}.tar.gz"
  log.info("Downloading #{file_to_download}.")
  object = BUCKET.objects[file_to_download]
  File.open(File.join(DATA_DIR, file_to_download), 'w') do |f|
    object.read do |chunk|
      f.write(chunk)
    end
  end
  log.info("Downloaded #{file_to_download}.")
  latest_timestamp += SECONDS_PER_DAY
end
