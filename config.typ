// Course metadata shim.
//
// The actual values live in `config.toml` (copied from `config.toml.example`
// by `/bootstrap`). This file just loads them and re-exports each field so
// templates can keep doing `#import "../config.typ": course-code, ...`.
//
// Edit `config.toml`, not this file.

#let _cfg = toml("config.toml")

#let course-code      = _cfg.at("course-code")
#let course-name      = _cfg.at("course-name")
#let textbook-author  = _cfg.at("textbook-author")
#let textbook-title   = _cfg.at("textbook-title")
#let textbook-edition = _cfg.at("textbook-edition")
#let instructor       = _cfg.at("instructor")
#let institution      = _cfg.at("institution")
#let zulip-stream     = _cfg.at("zulip-stream", default: "")

#let _short = _cfg.at("textbook-short", default: "")
#let textbook-short = if _short == "" { textbook-author } else { _short }
