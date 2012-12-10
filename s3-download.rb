#!/usr/bin/env ruby

require 'date'

DATA_DIR = File.expand_path('../data', __FILE__)

# enforce there is a `data` directory
if !File.directory? DATA_DIR
  abort(DATA_DIR + ' does not exist!')
end

# Get the timestamp latest file.
previous_data = Dir.entries(DATA_DIR)
latest_timestamp = 0
previous_data.each do |data|
  match_data = /\d{4}-\d{2}-\d{2}/.match(data)
  if !!match_data
    timestamp = Date.parse(match_data.to_s).to_time.to_i
    if timestamp > latest_timestamp
      latest_timestamp = timestamp
    end
  else
    p 'Invalid file name: ' + data
  end
end

# Start to download.
SECOND_PER_DAY = 24 * 3600
today_timestamp = Date.today.to_time.to_i
s3 = AWS::S3.new(ENV['AWS_ACCESS_KEY_ID'], ENV['AWS_SECRET_ACCESS_KEY'])
BUCKET = s3.buckets.['weather-data-compilation']
while latest_timestamp < today_timestamp do
  latest_timestamp += SECOND_PER_DAY
  file_to_download = "weather-data-#{Time.at(latest_timestamp).strftime('%Y-%m-%d')}.tar.gz"
  object = BUCKET.objects[file_to_download]
  File.open(File.join(DATA_DIR, file_to_download), 'w') do |f|
    object.read do |chunk|
      f.write(chunk)
    end
  end
  p 'Downloaded ' + file_to_download
end
