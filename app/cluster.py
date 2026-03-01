import time, threading, random, requests

class RaftNode:
    def __init__(self):
        self.node_id = None
        self.node_url = None
        self.state = "FOLLOWER"
        self.current_term = 0
        self.voted_for = None
        self.log = []
        self.commit_index = 0
        self.peers = {} 
        self.heartbeat_timer = None
        self.lock = threading.Lock()

    def init_node(self, node_id, node_url, peer_list):
        """Initialize node with config values so it doesn't need Flask context later."""
        self.node_id = node_id
        self.node_url = node_url
        for p in peer_list:
            if p and "=" in p:
                name, url = p.split("=")
                self.peers[name] = url

    def start_election_timer(self):
        if self.heartbeat_timer: self.heartbeat_timer.cancel()
        timeout = random.uniform(0.15, 0.3)
        self.heartbeat_timer = threading.Timer(timeout, self.become_candidate)
        self.heartbeat_timer.start()

    def become_candidate(self):
        with self.lock:
            self.state = "CANDIDATE"
            self.current_term += 1
            self.voted_for = self.node_id # Use self instead of current_app
            print(f"Node {self.node_id} becoming Candidate for Term {self.current_term}")
        
        votes = 1 
        for name, url in self.peers.items():
            try:
                resp = requests.post(f"{url}/raft/request_vote", json={
                    "term": self.current_term,
                    "candidate_id": self.node_id
                }, timeout=0.1)
                if resp.json().get("vote_granted"): votes += 1
            except: pass
        
        if votes > (len(self.peers) + 1) / 2:
            self.become_leader()
        else:
            self.start_election_timer()

    def become_leader(self):
        with self.lock:
            self.state = "LEADER"
            print(f"--- Node {self.node_id} ELECTED LEADER ---")
        self.send_heartbeats()

    def send_heartbeats(self):
        if self.state != "LEADER": return
        for name, url in self.peers.items():
            try:
                requests.post(f"{url}/raft/append_entries", json={
                    "term": self.current_term,
                    "leader_id": self.node_id,
                    "commit_index": self.commit_index
                }, timeout=0.05)
            except: pass
        # Schedule next heartbeat
        threading.Timer(0.05, self.send_heartbeats).start()

raft = RaftNode()