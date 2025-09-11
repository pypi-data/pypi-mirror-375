import { aA as p, aJ as P } from "./mermaid.core-VANNf1YM.js";
import { f as I, h as m, j as w, l as y, m as g, n as o, k as A, o as N, p as E, q as M, r as _, s as O, t as $, u as c, v as B, w as F } from "./Index-HF_NH3zS.js";
import { c as T, d as S } from "./_baseUniq-BKbRBgpx.js";
var l = /\s/;
function q(r) {
  for (var n = r.length; n-- && l.test(r.charAt(n)); )
    ;
  return n;
}
var G = /^\s+/;
function H(r) {
  return r && r.slice(0, q(r) + 1).replace(G, "");
}
var v = NaN, L = /^[-+]0x[0-9a-f]+$/i, R = /^0b[01]+$/i, z = /^0o[0-7]+$/i, C = parseInt;
function J(r) {
  if (typeof r == "number")
    return r;
  if (I(r))
    return v;
  if (m(r)) {
    var n = typeof r.valueOf == "function" ? r.valueOf() : r;
    r = m(n) ? n + "" : n;
  }
  if (typeof r != "string")
    return r === 0 ? r : +r;
  r = H(r);
  var t = R.test(r);
  return t || z.test(r) ? C(r.slice(2), t ? 2 : 8) : L.test(r) ? v : +r;
}
var x = 1 / 0, K = 17976931348623157e292;
function W(r) {
  if (!r)
    return r === 0 ? r : 0;
  if (r = J(r), r === x || r === -x) {
    var n = r < 0 ? -1 : 1;
    return n * K;
  }
  return r === r ? r : 0;
}
function X(r) {
  var n = W(r), t = n % 1;
  return n === n ? t ? n - t : n : 0;
}
var b = Object.prototype, Y = b.hasOwnProperty, sr = p(function(r, n) {
  r = Object(r);
  var t = -1, e = n.length, a = e > 2 ? n[2] : void 0;
  for (a && P(n[0], n[1], a) && (e = 1); ++t < e; )
    for (var f = n[t], i = w(f), s = -1, d = i.length; ++s < d; ) {
      var u = i[s], h = r[u];
      (h === void 0 || y(h, b[u]) && !Y.call(r, u)) && (r[u] = f[u]);
    }
  return r;
});
function D(r) {
  return function(n, t, e) {
    var a = Object(n);
    if (!g(n)) {
      var f = o(t);
      n = A(n), t = function(s) {
        return f(a[s], s, a);
      };
    }
    var i = r(n, t, e);
    return i > -1 ? a[f ? n[i] : i] : void 0;
  };
}
var Q = Math.max;
function U(r, n, t) {
  var e = r == null ? 0 : r.length;
  if (!e)
    return -1;
  var a = t == null ? 0 : X(t);
  return a < 0 && (a = Q(e + a, 0)), T(r, o(n), a);
}
var fr = D(U);
function Z(r, n) {
  var t = -1, e = g(r) ? Array(r.length) : [];
  return S(r, function(a, f, i) {
    e[++t] = n(a, f, i);
  }), e;
}
function dr(r, n) {
  var t = E(r) ? N : Z;
  return t(r, o(n));
}
var V = Object.prototype, k = V.hasOwnProperty;
function j(r, n) {
  return r != null && k.call(r, n);
}
function ur(r, n) {
  return r != null && M(r, n, j);
}
function rr(r, n) {
  return r < n;
}
function nr(r, n, t) {
  for (var e = -1, a = r.length; ++e < a; ) {
    var f = r[e], i = n(f);
    if (i != null && (s === void 0 ? i === i && !I(i) : t(i, s)))
      var s = i, d = f;
  }
  return d;
}
function hr(r) {
  return r && r.length ? nr(r, _, rr) : void 0;
}
function tr(r, n, t, e) {
  if (!m(r))
    return r;
  n = O(n, r);
  for (var a = -1, f = n.length, i = f - 1, s = r; s != null && ++a < f; ) {
    var d = $(n[a]), u = t;
    if (d === "__proto__" || d === "constructor" || d === "prototype")
      return r;
    if (a != i) {
      var h = s[d];
      u = void 0, u === void 0 && (u = m(h) ? h : c(n[a + 1]) ? [] : {});
    }
    B(s, d, u), s = s[d];
  }
  return r;
}
function mr(r, n, t) {
  for (var e = -1, a = n.length, f = {}; ++e < a; ) {
    var i = n[e], s = F(r, i);
    t(s, i) && tr(f, O(i, r), s);
  }
  return f;
}
export {
  rr as a,
  nr as b,
  Z as c,
  mr as d,
  hr as e,
  fr as f,
  sr as g,
  ur as h,
  X as i,
  dr as m,
  W as t
};
