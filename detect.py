# detect.py - security guard: catches prompt injection and dangerous behaviour
import re, json

INJECTION = [r"ignore (all |any )?(previous|prior|above) instructions", r"disregard .{0,40}instructions",
             r"new instructions", r"system (notice|override|prompt)", r"do not (tell|inform) the user",
             r"you are now", r"reveal .{0,30}(password|secret|key)"]
SENSITIVE = ["secret", "password", ".env", "id_rsa", "/etc/passwd", "api_key", "credential"]
DANGEROUS = ["rm -rf", "curl ", "wget ", "chmod", "sudo", "nc ", "base64 -d"]

def scan_output(text):
    """Tool output is untrusted data: look for hidden instructions in it"""
    t = str(text).lower()
    return [f"prompt_injection ('{m.group(0)[:40]}')" for p in INJECTION if (m := re.search(p, t))]

def check_call(tool, args):
    """Check a requested tool call BEFORE it runs"""
    s, out = json.dumps(args).lower(), []
    p = str(args.get("path", ""))
    if ".." in p or p.startswith(("/", "~")): out.append(f"path_traversal ({p})")
    out += [f"sensitive_access ('{k}')" for k in SENSITIVE if k in s][:1]
    out += [f"dangerous_command ('{k.strip()}')" for k in DANGEROUS if k in s][:1]
    return out

LEAK = r"(password|passwd|secret|api[_-]?key|token)\s*[=:]\s*\S+"

def scan_leak(text):
    """Did the agent repeat a credential in its own reply? (data leak / exfiltration)"""
    m = re.search(LEAK, str(text).lower())
    return [f"data_leak ('{m.group(1)}' value repeated in agent reply)"] if m else []