import armaclass

# From https://community.bistudio.com/wiki/server.cfg
server_cfg = '''
//
// server.cfg
//
// comments are written with "//" in front of them.


// GLOBAL SETTINGS
hostname = "Fun and Test Server";		// The name of the server that shall be displayed in the public server list
password = "";							// Password for joining, eg connecting to the server
passwordAdmin = "xyz";					// Password to become server admin. When you're in Arma MP and connected to the server, type '#login xyz'
serverCommandPassword = "xyzxyz";		// Password required by alternate syntax of [[serverCommand]] server-side scripting.

//reportingIP = "armedass.master.gamespy.com";	// For ArmA1 publicly list your server on GameSpy. Leave empty for private servers
//reportingIP = "arma2pc.master.gamespy.com";	// For Arma 2 publicly list your server on GameSpy. Leave empty for private servers
//reportingIP = "arma2oapc.master.gamespy.com";	// For Arma2: Operation Arrowhead //this option is deprecated since A2: OA version 1.63
//reportingIP = "arma3" //not used at all
logFile = "server_console.log";			// Tells ArmA-server where the logfile should go and what it should be called


// WELCOME MESSAGE ("message of the day")
// It can be several lines, separated by comma
// Empty messages "" will not be displayed at all but are only for increasing the interval
motd[] = {
    "", "",
    "Two empty lines above for increasing interval",
    "Welcome to our server",
    "", "",
    "We are looking for fun - Join us Now !",
    "http://www.example.com",
    "One more empty line below for increasing interval",
    ""
};
motdInterval = 5;					// Time interval (in seconds) between each message


// JOINING RULES
//checkfiles[] = {};				// Outdated.
maxPlayers = 64;					// Maximum amount of players. Civilians and watchers, beholder, bystanders and so on also count as player.
kickDuplicate = 1;					// Each ArmA version has its own ID. If kickDuplicate is set to 1, a player will be kicked when he joins a server where another player with the same ID is playing.
verifySignatures = 2;				// Verifies .pbos against .bisign files. Valid values 0 (disabled), 1 (prefer v2 sigs but accept v1 too) and 2 (only v2 sigs are allowed).
equalModRequired = 0;				// Outdated. If set to 1, player has to use exactly the same -mod= startup parameter as the server.
allowedFilePatching = 0;			// Allow or prevent client using -filePatching to join the server. 0, is disallow, 1 is allow HC, 2 is allow all clients (since Arma 3 1.49+)
filePatchingExceptions[] = {"123456789","987654321"}; // Whitelisted Steam IDs allowed to join with -filePatching enabled
//requiredBuild = 12345;			// Require clients joining to have at least build 12345 of game, preventing obsolete clients to connect


// VOTING
voteMissionPlayers = 1;				// Tells the server how many people must connect so that it displays the mission selection screen.
voteThreshold = 0.33;				// 33% or more players need to vote for something, for example an admin or a new map, to become effective


// INGAME SETTINGS
disableVoN = 0;					// If set to 1, Voice over Net will not be available
vonCodec = 1; 					// If set to 1 then it uses IETF standard OPUS codec, if to 0 then it uses SPEEX codec (since Arma 3 update 1.58+)
vonCodecQuality = 30;			// since 1.62.95417 supports range 1-20 //since 1.63.x will supports range 1-30 //8kHz is 0-10, 16kHz is 11-20, 32kHz(48kHz) is 21-30
persistent = 1;					// If 1, missions still run on even after the last player disconnected.
timeStampFormat = "short";		// Set the timestamp format used on each report line in server-side RPT file. Possible values are "none" (default),"short","full".
BattlEye = 1;					// Server to use BattlEye system
allowedLoadFileExtensions[] = {"hpp","sqs","sqf","fsm","cpp","paa","txt","xml","inc","ext","sqm","ods","fxy","lip","csv","kb","bik","bikb","html","htm","biedi"}; //only allow files with those extensions to be loaded via loadFile command (since Arma 3 build 1.19.124216)
allowedPreprocessFileExtensions[] = {"hpp","sqs","sqf","fsm","cpp","paa","txt","xml","inc","ext","sqm","ods","fxy","lip","csv","kb","bik","bikb","html","htm","biedi"}; //only allow files with those extensions to be loaded via preprocessFile/preprocessFileLineNumber commands (since Arma 3 build 1.19.124323)
allowedHTMLLoadExtensions[] = {"htm","html","xml","txt"}; //only allow files with those extensions to be loaded via HTMLLoad command (since Arma 3 build 1.27.126715)
//allowedHTMLLoadURIs[] = {}; // Leave commented to let missions/campaigns/addons decide what URIs are supported. Uncomment to define server-level restrictions for URIs

// TIMEOUTS
disconnectTimeout = 5;			// Time to wait before disconnecting a user which temporarly lost connection. Range is 5 to 90 seconds.
maxDesync = 150;				// Max desync value until server kick the user
maxPing= 200;					// Max ping value until server kick the user
maxPacketLoss= 50;				// Max packetloss value until server kick the user
kickClientsOnSlowNetwork[] = { 0, 0, 0, 0 }; // Defines if {<MaxPing>, <MaxPacketLoss>, <MaxDesync>, <DisconnectTimeout>} will be logged (0) or kicked (1)
kickTimeout[] = { {0, -1}, {1, 180}, {2, 180}, {3, 180} };
votingTimeOut[] = {60, 90};		// Kicks users from server if they spend too much time in mission voting
roleTimeOut[] = {90, 120};		// Kicks users from server if they spend too much time in role selection
briefingTimeOut[] = {60, 90};	// Kicks users from server if they spend too much time in briefing (map) screen
debriefingTimeOut[] = {45, 60};	// Kicks users from server if they spend too much time in debriefing screen
lobbyIdleTimeout = 300;			// The amount of time the server will wait before force-starting a mission without a logged-in Admin.


// SCRIPTING ISSUES
onUserConnected = "";
onUserDisconnected = "";
doubleIdDetected = "";
//regularCheck = "{}";				// Server checks files from time to time by hashing them and comparing the hash to the hash values of the clients. //deprecated

// SIGNATURE VERIFICATION
onUnsignedData = "kick (_this select 0)";	// unsigned data detected
onHackedData = "kick (_this select 0)";		// tampering of the signature detected
onDifferentData = "";				// data with a valid signature, but different version than the one present on server detected


// MISSIONS CYCLE (see below)
randomMissionOrder = true;	// Randomly iterate through Missions list
autoSelectMission = true;	// Server auto selects next mission in cycle

class Missions
{
    class TestMission01
    {
        template = MP_Marksmen_01.Altis;
        difficulty = "veteran";
        class Params {};
    };
    class TestMission02
    {
        template = MP_End_Game_01.Altis;
        difficulty = "veteran";
        class Params {};
    };
    class TestMission03
    {
        template = MP_End_Game_02.Altis;
        difficulty = "veteran";
        class Params {};
    };
    class TestMission04
    {
        template = MP_End_Game_03.Altis;
        difficulty = "veteran";
        class Params {};
    };
};

missionWhitelist[] = {};	// An empty whitelist means there is no restriction on what missions' available
'''


def test_server_cfg():
    server_parsed = armaclass.parse(server_cfg)
    generated = armaclass.generate(server_parsed)
    assert server_parsed == armaclass.parse(generated)
