from discord.ext import commands
import discord
from .utils import db

class Settings(db.Table):
    id = db.Column(db.Integer(big=True), primary_key=True)
    logging_enabled = db.Column(db.Boolean, default=False)