require 'optparse'

options = {:subdomain => 'defaultdomain', :port => 3000}

parser = OptionParser.new do|opts|
    opts.banner = "Usage: localtunnel.rb [options]"
    opts.on('-s', '--subdomain subdomain', 'Subdomain') do |subdomain|
        options[:subdomain] = subdomain;
    end

    opts.on('-p', '--port port', 'Port') do |port|
        options[:port] = port;
    end

    opts.on('-h', '--help', 'Displays Help') do
        puts opts
        exit
    end
end

parser.parse!

def ordinal(number)
  abs_number = number.to_i.abs

  if (11..13).include?(abs_number % 100)
    "th"
  else
    case abs_number % 10
      when 1; "st"
      when 2; "nd"
      when 3; "rd"
      else    "th"
    end
  end
end

def ordinalize(number)
  "#{number}#{ordinal(number)}"
end

launch_count = 0

while true
    launch_count += 1
    puts "Running localtunnel for the #{ordinalize(launch_count)} time"
    `lt --port #{options[:port]} --subdomain #{options[:subdomain]}`
end