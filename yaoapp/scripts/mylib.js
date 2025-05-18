// yao run scripts.mylib.test
function test() {
  let output = Process("plugins.myplugin.hello");
  console.log(output);
}

// yao run scripts.mylib.hello
function hello(name) {
  let output = Process("plugins.py.hello", name);
  return output;
}

// yao run scripts.mylib.embed "你好"
function embed(name) {
  let output = Process("plugins.py.embed", name);
  return output;
}
