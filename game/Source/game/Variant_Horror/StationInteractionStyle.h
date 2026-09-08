#pragma once

#include "Brushes/SlateColorBrush.h"

/** Shared station interaction palette: aged brass, warm ink, square double rules. */
namespace StationInteractionStyle
{
 inline const FSlateColorBrush OuterRule(FLinearColor(.58f,.40f,.16f,.95f));
 inline const FSlateColorBrush RuleGap(FLinearColor(.045f,.031f,.018f,.97f));
 inline const FSlateColorBrush InnerRule(FLinearColor(.27f,.18f,.075f,.95f));
 inline const FSlateColorBrush Panel(FLinearColor(.055f,.040f,.024f,.95f));
 inline const FSlateColorBrush Key(FLinearColor(.72f,.56f,.30f,1.f));
 inline const FLinearColor Ink(.055f,.037f,.017f,1.f);
 inline const FLinearColor Action(.91f,.78f,.53f,1.f);
 inline const FLinearColor Detail(.59f,.46f,.28f,1.f);
}
